from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.dependencies import get_catalog_service, get_current_session, require_admin
from api.openapi_errors import (
    FORBIDDEN_ADMIN_RESPONSE,
    NOT_FOUND_PRODUCT_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    UNPROCESSABLE_RESPONSE,
)
from models import Product, UserSession
from schemas.requests import ProductCreateRequest, ProductPatchRequest
from schemas.responses import ProductResponse
from services.catalog_service import CatalogService
from services.exceptions import NotFoundError, ValidationError

router = APIRouter(tags=["Products"])


def _to_product_response(product: Product) -> ProductResponse:
    return ProductResponse.model_validate(product.model_dump())


@router.get(
    "/products",
    response_model=list[ProductResponse],
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def list_products(
    _: Annotated[UserSession, Depends(get_current_session)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[ProductResponse]:
    products = catalog.list_products_sorted()
    return [_to_product_response(product) for product in products]


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **UNAUTHORIZED_RESPONSE,
        **FORBIDDEN_ADMIN_RESPONSE,
        **UNPROCESSABLE_RESPONSE,
    },
)
async def create_product(
    payload: ProductCreateRequest,
    _: Annotated[UserSession, Depends(require_admin)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    try:
        product = catalog.create_product(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    return _to_product_response(product)


@router.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
    responses={
        **UNAUTHORIZED_RESPONSE,
        **FORBIDDEN_ADMIN_RESPONSE,
        **NOT_FOUND_PRODUCT_RESPONSE,
        **UNPROCESSABLE_RESPONSE,
    },
)
async def patch_product(
    product_id: int,
    payload: ProductPatchRequest,
    _: Annotated[UserSession, Depends(require_admin)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ProductResponse:
    try:
        product = catalog.patch_product(product_id=product_id, payload=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    return _to_product_response(product)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **UNAUTHORIZED_RESPONSE,
        **FORBIDDEN_ADMIN_RESPONSE,
        **NOT_FOUND_PRODUCT_RESPONSE,
    },
)
async def delete_product(
    product_id: int,
    _: Annotated[UserSession, Depends(require_admin)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> Response:
    try:
        catalog.delete_product(product_id=product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
