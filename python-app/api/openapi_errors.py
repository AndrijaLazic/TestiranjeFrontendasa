from __future__ import annotations

from typing import Any


def _json_response(description: str, examples: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "examples": examples,
            }
        },
    }


INVALID_CREDENTIALS_RESPONSE = {
    401: _json_response(
        "Invalid username or password",
        {
            "invalid_credentials": {
                "summary": "Incorrect login credentials",
                "value": {"detail": "Invalid username or password"},
            }
        },
    )
}

UNAUTHORIZED_RESPONSE = {
    401: _json_response(
        "Missing or invalid bearer token",
        {
            "missing_token": {
                "summary": "Authorization header is missing",
                "value": {"detail": "Missing bearer token"},
            },
            "invalid_token": {
                "summary": "Token is not known by the API",
                "value": {"detail": "Invalid bearer token"},
            },
        },
    )
}

FORBIDDEN_ADMIN_RESPONSE = {
    403: _json_response(
        "Forbidden",
        {
            "admin_required": {
                "summary": "User does not have admin role",
                "value": {"detail": "Admin role required"},
            }
        },
    )
}

NOT_FOUND_PRODUCT_RESPONSE = {
    404: _json_response(
        "Product not found",
        {
            "product_not_found": {
                "summary": "Requested product does not exist",
                "value": {"detail": "Product not found"},
            }
        },
    )
}

NOT_FOUND_CATEGORY_RESPONSE = {
    404: _json_response(
        "Category not found",
        {
            "category_not_found": {
                "summary": "Requested category does not exist",
                "value": {"detail": "Category not found"},
            }
        },
    )
}

UNPROCESSABLE_RESPONSE = {
    422: _json_response(
        "Validation error",
        {
            "request_validation": {
                "summary": "Request schema validation failed",
                "value": {
                    "detail": [
                        {
                            "loc": ["body", "price"],
                            "msg": "Input should be greater than or equal to 0",
                            "type": "greater_than_equal",
                        }
                    ]
                },
            },
            "business_validation": {
                "summary": "Business rule validation failed",
                "value": {"detail": "Invalid sub_category_id for the provided category_id"},
            },
        },
    )
}
