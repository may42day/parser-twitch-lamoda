from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.lamoda.repository import (
    clear_categories_data,
    get_categories,
    get_lowest_subcategories,
    get_product_info,
    get_specific_category,
    get_subcategories,
)
from src.lamoda.utils import prepare_response_data
from src.lamoda.service import parse_all_categories
from src.resources.kafka import producer_send_one

router = APIRouter()


@router.get("/auto-parse")
@cache(expire=1200)
async def parse_categories():
    """
    API to start auto-parsing all categories.

    Clears all lamoda data and then starts parsing of all categories.
    """
    await clear_categories_data()
    await producer_send_one(parse_all_categories)

    return {"message": "Parsing started"}


@router.get("/categories/clear")
async def clear_categories():
    """
    API to clear all lamoda data.

    Returns message with amount of cleared categories.
    """
    count = await clear_categories_data()
    return {"message": f"Categories cleared ({count})"}


@router.get("/categories")
@cache(expire=60)
async def categories():
    """
    API to gel all categories.
    """
    categories = await get_categories()
    await prepare_response_data(categories)
    return {"data": categories}


@router.get("/{category}")
@cache(expire=60)
async def specific_category(category: str):
    """
    API to get data of specific category.

    Parameters:
    - category (str, required) - category name.
    """
    data = await get_specific_category(category)
    await prepare_response_data(data)

    return {"data": data}


@router.get("/{category}/{subcategory_slug}")
@cache(expire=60)
async def subcategories(category: str, subcategory_slug: str):
    """
    API to get data of specific subcategory.

    Parameters:
    - category (str, required) - category name.
    - subcategory_slug (str, required) - subcategory slug.
    """
    data = await get_subcategories(category, subcategory_slug)
    await prepare_response_data(data)

    return {"data": data}


@router.get("/{category}/{subcategory_slug}/{low_subcategory_slug}")
@cache(expire=60)
async def lowest_subcategories(
    category: str, subcategory_slug: str, low_subcategory_slug: str
):
    """
    API to get data of specific low-level subcategory.

    Parameters:
    - category (str, required) - category name.
    - subcategory_slug (str, required) - subcategory slug.
    - low_subcategory_slug (str, required) - low-level subcategory slug.
    """
    data = await get_lowest_subcategories(
        category, subcategory_slug, low_subcategory_slug
    )
    await prepare_response_data(data)
    return {"data": data}


@router.get("/{category}/{subcategory_slug}/{low_subcategory_slug}/{product_number}")
@cache(expire=60)
async def product_info(
    category: str, subcategory_slug: str, low_subcategory_slug: str, product_number: str
):
    """
    API to get product data.

    Parameters:
    - category (str, required) - category name.
    - subcategory_slug (str, required) - subcategory slug.
    - low_subcategory_slug (str, required) - low-level subcategory slug.
    - product_number (str, required) - product article number.
    """
    data = await get_product_info(
        category, subcategory_slug, low_subcategory_slug, product_number
    )
    await prepare_response_data(data)
    return {"data": data}
