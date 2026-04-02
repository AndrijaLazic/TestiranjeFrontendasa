from __future__ import annotations

from secrets import token_urlsafe

from models import UserSession
from services.exceptions import ForbiddenError, UnauthorizedError
from state.store import InMemoryStore


class AuthService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def login(self, username: str, password: str) -> tuple[str, UserSession]:
        user_record = self.store.users.get(username)
        if user_record is None or user_record.password != password:
            raise UnauthorizedError("Invalid username or password")

        access_token = token_urlsafe(32)
        session = UserSession(username=username, role=user_record.role)
        self.store.tokens[access_token] = session
        return access_token, session

    def get_session_by_token(self, access_token: str) -> UserSession | None:
        return self.store.tokens.get(access_token)

    def ensure_admin(self, session: UserSession) -> None:
        if session.role != "admin":
            raise ForbiddenError("Admin role required")
