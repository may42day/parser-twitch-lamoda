from typing import List, Dict
from src.resources.mongo import db_twitch
from src.twitch.utils import add_current_time

db = db_twitch.categories


async def insert_categories_data(data: List[Dict]) -> List[str]:
    """
    Multiple insert category/game data to Twitch categories/games collection.

    Args:
    - data (list of dicts) - list of categories info.
    """
    await add_current_time(data)
    inserted_data = await db.insert_many(data)

    inserted_ids = [str(item_id) for item_id in inserted_data.inserted_ids]
    return inserted_ids


async def get_categories_data() -> List[Dict]:
    """
    Get all data from Twitch categories/games collection.
    """
    result = await db.find({}).to_list(None)
    return result


async def get_category_data(object_id: int = None, category_id: int = None) -> Dict:
    """
    Get specific category data from Twitch categories/games collection.

    Args:
    - object_id (int, optional) - category object id in database.
    - category_id (int, optional) - category id.
    """
    if not object_id and not category_id:
        return None

    if object_id:
        result = await db.find_one({"_id": object_id})
    elif category_id:
        result = await db.find_one({"id": str(category_id)})

    return result


async def clear_categories_data() -> int:
    """
    Clear all data from Twitch categories/games collection.
    """
    count = await db.delete_many({})
    return count.deleted_count
