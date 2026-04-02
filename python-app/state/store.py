from __future__ import annotations

from models import Category, Product, SubCategory, UserRecord, UserSession

CATEGORY_DEFINITIONS: dict[int, tuple[str, list[str]]] = {
    1: ("CPU", ["Entry", "Gaming", "Workstation", "Server"]),
    2: ("GPU", ["Entry", "Gaming", "Professional", "Blower"]),
    3: ("Motherboard", ["Mini-ITX", "Micro-ATX", "ATX", "E-ATX"]),
    4: ("Memory", ["DDR4", "DDR5", "SO-DIMM DDR4", "SO-DIMM DDR5"]),
    5: ("Storage", ["HDD", "SATA SSD", "NVMe SSD", "External"]),
}

DEFAULT_USERS: dict[str, UserRecord] = {
    "admin": UserRecord(password="admin123", role="admin"),
    "user": UserRecord(password="user123", role="user"),
}


class InMemoryStore:
    def __init__(self) -> None:
        (
            self.categories,
            self.category_by_id,
            self.subcategories_by_category_id,
            self.subcategory_by_id,
        ) = self._build_taxonomy()
        self.users = {username: user.model_copy(deep=True) for username, user in DEFAULT_USERS.items()}
        self.tokens: dict[str, UserSession] = {}
        self.products_by_id: dict[int, Product] = {}
        self.next_product_id = 1
        self.reset_state()

    def _build_taxonomy(
        self,
    ) -> tuple[list[Category], dict[int, Category], dict[int, list[SubCategory]], dict[int, SubCategory]]:
        categories: list[Category] = []
        category_by_id: dict[int, Category] = {}
        subcategories_by_category_id: dict[int, list[SubCategory]] = {}
        subcategory_by_id: dict[int, SubCategory] = {}

        for category_id, (category_name, subcategory_names) in CATEGORY_DEFINITIONS.items():
            category = Category(id=category_id, name=category_name)
            categories.append(category)
            category_by_id[category_id] = category

            category_subcategories: list[SubCategory] = []
            for index, subcategory_name in enumerate(subcategory_names, start=1):
                subcategory_id = (category_id * 100) + index
                subcategory = SubCategory(
                    id=subcategory_id,
                    category_id=category_id,
                    name=subcategory_name,
                )
                category_subcategories.append(subcategory)
                subcategory_by_id[subcategory_id] = subcategory

            subcategories_by_category_id[category_id] = category_subcategories

        return categories, category_by_id, subcategories_by_category_id, subcategory_by_id

    def _seed_products(self) -> dict[int, Product]:
        seeded_products: dict[int, Product] = {}
        product_id = 1

        for category in self.categories:
            subcategories = self.subcategories_by_category_id[category.id]
            for sub_index, subcategory in enumerate(subcategories, start=1):
                base_price = (category.id * 75.0) + (sub_index * 15.0)
                for model_number in range(1, 51):
                    price = round(base_price + (model_number * 4.5), 2)
                    seeded_products[product_id] = Product(
                        id=product_id,
                        category_id=category.id,
                        category=category.name,
                        sub_category_id=subcategory.id,
                        sub_category=subcategory.name,
                        price=price,
                        name=f"{category.name} {subcategory.name} Model {model_number:02d}",
                    )
                    product_id += 1

        return seeded_products

    def reset_state(self) -> None:
        self.products_by_id = self._seed_products()
        self.next_product_id = max(self.products_by_id, default=0) + 1
        self.tokens = {}

    def allocate_product_id(self) -> int:
        product_id = self.next_product_id
        self.next_product_id += 1
        return product_id
