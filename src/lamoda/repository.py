from typing import Dict, List
from bson import ObjectId
from src.exceptions.exc_types import LamodaCategoriesNotFoundException

from src.lamoda.utils import add_current_time
from src.resources.mongo import db_lamoda

db = db_lamoda


async def insert_main_categories(data: List[Dict]) -> List:
    """
    Function to insert basic data about main categories (men, women, kids).

    Returns IDs of inserter items.

    Args:
    - data (list of dicts) - categories info.
    """
    await add_current_time(data)
    result = await db.insert_many(data)

    inserted_ids = [str(item_id) for item_id in result.inserted_ids]
    return inserted_ids


async def clear_categories_data() -> int:
    """
    Clear all data from lamoda collection.

    Returns amount of deleted instances.
    """
    count = await db.delete_many({})
    return count.deleted_count


async def update_category_by_id(object_id: ObjectId, field_name: str, data: dict):
    """
    Updates 2-level categories with provided field name and its data.

    Args:
    - object_id (ObjectId) - category id in database.
    - field_name (str) - name of new field.
    - data (dict) - category info to save in new field.
    """
    filter_query = {"categories._id": object_id}

    parent = await db.find_one(filter_query)
    if parent:
        for category in parent.get("categories", []):
            if category["_id"] == object_id:
                await add_current_time(data)
                insert_query = {"$set": {f"categories.$.{field_name}": data}}
                await db.update_one(filter_query, insert_query)
                break


async def insert_product_items(items: List[Dict], subcategory_id: ObjectId):
    """
    Inserts product's data to subcategory.

    Args:
    - items (List[Dict]) - list of products info.
    - subcategory_id (ObjectId) - category id in database.
    """
    filter_query = {"categories.categories._id": subcategory_id}
    parent = await db.find_one(filter_query)

    if parent:
        for top_id, category in enumerate(parent.get("categories", [])):
            for middle_id, subcategory in enumerate(category.get("categories", [])):
                if subcategory["_id"] == subcategory_id:
                    await add_current_time(items)
                    insert_query = {
                        "$set": {
                            f"categories.{top_id}.categories.{middle_id}.products": items
                        }
                    }
                    await db.update_one(filter_query, insert_query)
                    break


async def get_categories() -> List[Dict]:
    """
    Function to get main categories data.
    """
    result = await db.find({}, {"categories": 0}).to_list(length=None)
    return result


async def get_specific_category(category: str) -> List[Dict]:
    """
    Function to get data of specific category.

    Args:
    - category (str) - category name.
    """
    result = await db.find_one({"category": category})

    if not result:
        categories_data = await get_categories()
        if categories_data:
            categories = [c["category"] for c in categories_data]
            raise LamodaCategoriesNotFoundException(
                message=f"Category '{category}' not found", details=categories
            )
        else:
            raise LamodaCategoriesNotFoundException(message="No categories exists")

    for category in result["categories"]:
        if category.get("categories"):
            del category["categories"]
    return result


async def get_subcategories(
    category: str, subcategory_slug: str, exclude_products=True
) -> List[Dict]:
    """
    Function to get data of specific subcategory.

    Args:
    - category (str) - category name.
    - subcategory_slug (str) - subcategory slug.
    - exclude_products (bool, optional) - option to include or exclude products field.
    """
    filter_query = {
        "$and": [{"category": category}, {"categories.slug": subcategory_slug}]
    }
    parent = await db.find_one(filter_query, {"categories.$": 1})

    if not parent:
        category = await get_specific_category(category)
        subcategories = [c["slug"] for c in category.get("categories", [])]
        raise LamodaCategoriesNotFoundException(
            message=f"Subcategory '{subcategory_slug}' not found", details=subcategories
        )

    if parent and parent.get("categories"):
        subcategories = parent["categories"][0].get("categories")
        if subcategories and exclude_products:
            for category in subcategories:
                if category.get("products"):
                    del category["products"]
        return subcategories


async def get_lowest_subcategories(
    category: str, subcategory_slug: str, low_subcategory_slug: str
) -> List[Dict]:
    """
    Function to get data of specific low-level subcategory

    Args
    - category (str) - category name.
    - subcategory_slug (str) - subcategory slug.
    - low_subcategory_slug (str) - next subcategory slug.
    """
    subcategories = await get_subcategories(
        category, subcategory_slug, exclude_products=False
    )
    for category in subcategories:
        if category["slug"] == low_subcategory_slug:
            return category

    categories = [c["slug"] for c in subcategories]
    raise LamodaCategoriesNotFoundException(
        message=f"Subcategory '{low_subcategory_slug}' not found", details=categories
    )


async def get_product_info(
    category: str, subcategory_slug: str, low_subcategory_slug: str, product: str
) -> Dict:
    """
    Function to get data of specific product.

    Args
    - category (str) - category name.
    - subcategory_slug (str) - subcategory slug.
    - low_subcategory_slug (str) - next subcategory slug.
    - product (str) - product article number.
    """
    category = await get_lowest_subcategories(
        category, subcategory_slug, low_subcategory_slug
    )
    if category and category.get("products"):
        for item in category["products"]:
            if item["product_number"] == product:
                return item
