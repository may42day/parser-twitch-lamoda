from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.twitch.repository.streams_repository import (
    clear_streams_data,
    get_stream_data,
    get_streams_data,
)
from src.twitch.services.streams_services import (
    auto_parse_all_streams,
    parse_specific_streams,
)
from src.resources.kafka import producer_send_one

router = APIRouter()


@router.get("/auto-parse")
@cache(expire=1200)
async def auto_parse_streams():
    """
    API to start auto-parsing streams.

    Parses all streams for every game(category) in database.
    """

    await clear_streams_data()
    await producer_send_one(auto_parse_all_streams)
    return {"message": "Parsing started"}


@router.get("/parse")
@cache(expire=600)
async def parse_streams(
    game_id: str = None,
    user_id: str = None,
    user_login: str = None,
    language: str = None,
    after: str = None,
    before: str = None,
    first: int = None,
):
    """
    API to start parsing streams.

    Parses first 20 streams in descending order by the number of viewers by default.
    Can parse specific streams if additional options are specified.

    Args:
    - game_id - (str, optional) - a game (category) ID used to filter the list of streams.
    - user_id - (str, optional) - a user ID used to filter the list of streams.
    - user_login - (str, optional) - a user login name used to filter the list of streams.
    - language - (str, optional) - a language code used to filter the list of streams.
    - after (str, optional) - pagination param used to get the next page of results.
    - before (str, optional) - pagination param used to get the previous page of results.
    - first (int, optional, max 100) - the maximum number of items to return per page in the response.
    """

    await producer_send_one(
        parse_specific_streams,
        game_id,
        user_id,
        user_login,
        first,
        after,
        before,
        language,
    )
    return {"message": "Parsing started"}


@router.get("/")
@cache(expire=60)
async def get_streams():
    """
    API to get all streams data.
    """
    data = await get_streams_data()

    for item in data:
        item["_id"] = str(item["_id"])

    return data


@router.get("/clear")
async def clear_categories():
    """
    API to clear streams collection.
    """
    count = await clear_streams_data()
    return {"message": f"Categories cleared ({count})"}


@router.get("/{stream_id}")
@cache(expire=60)
async def get_specific_stream(stream_id: int):
    """
    API to get specific stream data.

    Args:
    - id (str) - stream id.
    """
    data = await get_stream_data(stream_id=stream_id)
    if data:
        del data["_id"]
    return data
