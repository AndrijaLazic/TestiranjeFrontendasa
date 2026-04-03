from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: Literal["admin", "user"]


class CategoryResponse(BaseModel):
    id: int
    name: str


class SubCategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str


class ProductSortedDTO(BaseModel):
    id: int
    category_id: int
    category_name: str
    subcategory_id: int
    subcategory_name: str
    price: float = Field(ge=0)
    name: str


class ProductResponse(BaseModel):
    id: int
    category_id: int
    category: str
    sub_category_id: int
    sub_category: str
    price: float = Field(ge=0)
    name: str
