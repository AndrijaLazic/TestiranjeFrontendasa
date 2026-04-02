from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class ProductCreateRequest(BaseModel):
    category_id: int
    sub_category_id: int
    price: float = Field(ge=0)
    name: str = Field(min_length=1)


class ProductPatchRequest(BaseModel):
    category_id: int | None = None
    sub_category_id: int | None = None
    price: float | None = Field(default=None, ge=0)
    name: str | None = Field(default=None, min_length=1)
