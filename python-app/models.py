from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Category(BaseModel):
    id: int
    name: str


class SubCategory(BaseModel):
    id: int
    category_id: int
    name: str


class Product(BaseModel):
    id: int
    category_id: int
    category: str
    sub_category_id: int
    sub_category: str
    price: float = Field(ge=0)
    name: str = Field(min_length=1)


class UserSession(BaseModel):
    username: str
    role: Literal["admin", "user"]


class UserRecord(BaseModel):
    password: str
    role: Literal["admin", "user"]
