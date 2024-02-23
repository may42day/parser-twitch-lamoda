from typing import List, Dict
from src.resources.mongo import db_twitch
from src.twitch.utils import add_current_time

db = db_twitch.streams


async def insert_streams_data(data: List[Dict]) -> List[str]:
    """
    Multiple insert streams data to Twitch streams collection.

    Args:
    - data (list of dicts) - list of streams info.
    """
    await add_current_time(data)
    inserted_data = await db.insert_many(data)

    inserted_ids = [str(item_id) for item_id in inserted_data.inserted_ids]
    return inserted_ids


async def get_streams_data() -> List[Dict]:
    """
    Get all data from Twitch streams collection.
    """
    result = await db.find({}).to_list(None)
    return result


async def get_stream_data(object_id: int = None, stream_id: int = None) -> Dict:
    """
    Get specific category data from Twitch streams collection.

    Args:
    - object_id (int, optional) - stream object id in database.
    - stream_id (int, optional) - stream id.
    """
    if not object_id and not stream_id:
        return None

    if object_id:
        result = await db.find_one({"_id": object_id})
    elif stream_id:
        result = await db.find_one({"id": str(stream_id)})

    return result


async def clear_streams_data() -> int:
    """
    Clear all data from Twitch streams collection.
    """
    count = await db.delete_many({})
    return count.deleted_count
