from __future__ import annotations

from models import Category, Product, SubCategory
from schemas.requests import ProductCreateRequest, ProductPatchRequest
from schemas.responses import ProductSortedDTO
from services.exceptions import NotFoundError, ValidationError
from state.store import InMemoryStore


class CatalogService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def list_categories(self) -> list[Category]:
        return self.store.categories

    def list_subcategories(self, category_id: int) -> list[SubCategory]:
        if category_id not in self.store.category_by_id:
            raise NotFoundError("Category not found")
        return self.store.subcategories_by_category_id[category_id]

    def list_products_sorted(self) -> list[ProductSortedDTO]:
        products = sorted(
            self.store.products_by_id.values(),
            key=lambda product: (product.category_id, product.sub_category_id, product.id),
        )
        return [self._to_sorted_product_dto(product) for product in products]

    def create_product(self, payload: ProductCreateRequest) -> Product:
        category, subcategory = self._validate_category_subcategory(
            category_id=payload.category_id,
            sub_category_id=payload.sub_category_id,
        )
        product_id = self.store.allocate_product_id()
        product = Product(
            id=product_id,
            category_id=category.id,
            category=category.name,
            sub_category_id=subcategory.id,
            sub_category=subcategory.name,
            price=payload.price,
            name=payload.name,
        )
        self.store.products_by_id[product.id] = product
        return product

    def patch_product(self, product_id: int, payload: ProductPatchRequest) -> Product:
        existing = self.store.products_by_id.get(product_id)
        if existing is None:
            raise NotFoundError("Product not found")

        updated = existing.model_copy(deep=True)
        if payload.name is not None:
            updated.name = payload.name
        if payload.price is not None:
            updated.price = payload.price

        next_category_id = payload.category_id if payload.category_id is not None else updated.category_id
        next_subcategory_id = (
            payload.sub_category_id if payload.sub_category_id is not None else updated.sub_category_id
        )
        category, subcategory = self._validate_category_subcategory(
            category_id=next_category_id,
            sub_category_id=next_subcategory_id,
        )
        updated.category_id = category.id
        updated.category = category.name
        updated.sub_category_id = subcategory.id
        updated.sub_category = subcategory.name

        self.store.products_by_id[product_id] = updated
        return updated

    def delete_product(self, product_id: int) -> None:
        if product_id not in self.store.products_by_id:
            raise NotFoundError("Product not found")
        del self.store.products_by_id[product_id]

    def _validate_category_subcategory(self, category_id: int, sub_category_id: int) -> tuple[Category, SubCategory]:
        category = self.store.category_by_id.get(category_id)
        if category is None:
            raise ValidationError("Invalid category_id")

        subcategory = self.store.subcategory_by_id.get(sub_category_id)
        if subcategory is None or subcategory.category_id != category_id:
            raise ValidationError("Invalid sub_category_id for the provided category_id")

        return category, subcategory

    @staticmethod
    def _to_sorted_product_dto(product: Product) -> ProductSortedDTO:
        return ProductSortedDTO(
            id=product.id,
            category_id=product.category_id,
            category_name=product.category,
            subcategory_id=product.sub_category_id,
            subcategory_name=product.sub_category,
            price=product.price,
            name=product.name,
        )
