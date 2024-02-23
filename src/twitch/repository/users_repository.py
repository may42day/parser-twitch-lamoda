from typing import List, Dict
from src.resources.mongo import db_twitch
from src.twitch.utils import add_current_time

db = db_twitch.users


async def insert_users_data(data: List[Dict]) -> List[str]:
    """
    Multiple insert users data to Twitch users collection.

    Args:
    - data (list of dicts) - list of users info.
    """
    await add_current_time(data)
    inserted_data = await db.insert_many(data)

    inserted_ids = [str(item_id) for item_id in inserted_data.inserted_ids]
    return inserted_ids


async def get_users_data() -> List[Dict]:
    """
    Get all data from Twitch users collection.
    """
    result = await db.find({}).to_list(None)
    return result


async def get_user_data(identifier: str) -> Dict:
    """
    Get specific users data from Twitch users collection.

    Args:
    - identifier (str) - user's id or login.
    """
    query = {
        "$or": [
            {"login": identifier},
            {"id": identifier},
        ]
    }
    user = await db.find_one(query)
    return user


async def clear_users_data() -> int:
    """
    Clear all data from Twitch users collection.
    """
    count = await db.delete_many({})
    return count.deleted_count
