from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models import UserSession
from services.auth_service import AuthService
from services.catalog_service import CatalogService
from services.exceptions import ForbiddenError
from state.store import InMemoryStore

store = InMemoryStore()
auth_service = AuthService(store)
catalog_service = CatalogService(store)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_service() -> AuthService:
    return auth_service


async def get_catalog_service() -> CatalogService:
    return catalog_service


async def get_current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserSession:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = auth.get_session_by_token(credentials.credentials)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


async def require_admin(
    current_session: Annotated[UserSession, Depends(get_current_session)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserSession:
    try:
        auth.ensure_admin(current_session)
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return current_session


def reset_state() -> None:
    store.reset_state()
