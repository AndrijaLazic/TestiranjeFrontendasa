from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_auth_service
from api.openapi_errors import INVALID_CREDENTIALS_RESPONSE, UNPROCESSABLE_RESPONSE
from schemas.requests import LoginRequest
from schemas.responses import TokenResponse
from services.auth_service import AuthService
from services.exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        **INVALID_CREDENTIALS_RESPONSE,
        **UNPROCESSABLE_RESPONSE,
    },
)
async def login(
    payload: LoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    try:
        access_token, session = auth.login(payload.username, payload.password)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return TokenResponse(access_token=access_token, role=session.role)
