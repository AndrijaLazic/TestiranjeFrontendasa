from __future__ import annotations

from fastapi import FastAPI

from api.dependencies import reset_state as reset_application_state
from api.routers.auth_router import router as auth_router
from api.routers.products_router import router as products_router
from api.routers.taxonomy_router import router as taxonomy_router

app = FastAPI(
    title="PC Components API",
    description="In-memory API for managing PC component products with role-based access.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url=None,
    openapi_url="/openapi.json",
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(taxonomy_router)


def reset_state() -> None:
    reset_application_state()
