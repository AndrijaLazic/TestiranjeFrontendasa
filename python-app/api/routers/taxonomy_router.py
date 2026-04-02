from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_catalog_service, get_current_session
from api.openapi_errors import NOT_FOUND_CATEGORY_RESPONSE, UNAUTHORIZED_RESPONSE
from models import Category, SubCategory, UserSession
from schemas.responses import CategoryResponse, SubCategoryResponse
from services.catalog_service import CatalogService
from services.exceptions import NotFoundError

router = APIRouter(tags=["Taxonomy"])


def _to_category_response(category: Category) -> CategoryResponse:
    return CategoryResponse.model_validate(category.model_dump())


def _to_subcategory_response(subcategory: SubCategory) -> SubCategoryResponse:
    return SubCategoryResponse.model_validate(subcategory.model_dump())


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def list_categories(
    _: Annotated[UserSession, Depends(get_current_session)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[CategoryResponse]:
    categories = catalog.list_categories()
    return [_to_category_response(category) for category in categories]


@router.get(
    "/categories/{category_id}/subcategories",
    response_model=list[SubCategoryResponse],
    responses={
        **UNAUTHORIZED_RESPONSE,
        **NOT_FOUND_CATEGORY_RESPONSE,
    },
)
async def list_subcategories(
    category_id: int,
    _: Annotated[UserSession, Depends(get_current_session)],
    catalog: Annotated[CatalogService, Depends(get_catalog_service)],
) -> list[SubCategoryResponse]:
    try:
        subcategories = catalog.list_subcategories(category_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [_to_subcategory_response(subcategory) for subcategory in subcategories]
