import asyncio

from src.resources.kafka import producer_send_one
from src.twitch.repository.categories_repository import get_categories_data
from src.twitch.utils import response_into_dict
from src.twitch.repository.streams_repository import insert_streams_data
from src.main import get_twitch_client


async def auto_parse_all_streams():
    """
    Function to start parsing streams of all games(categories).

    Creates kafka task to parse subcategories for each parsed category.
    """
    categories = await get_categories_data()
    for category in categories:
        await producer_send_one(full_parse_specific_category, category)


async def full_parse_specific_category(category: dict):
    """
    Function to parse all streams of specific game(category).

    Makes requests with incremental page untill no streams returns.
    """
    twitch_client = await get_twitch_client()
    buffer_inserts = []

    response = await twitch_client.make_request(
        url_name="GET_STREAMS",
        http_method="GET",
        query_params={
            "game_id": category["id"],
            "first": 100,
        },
    )
    data = await response_into_dict(response)

    if data:
        buffer_inserts.append(insert_streams_data(data))

        counter = 1
        while True:
            pagination = response.json().get("pagination")
            if pagination:
                response = await twitch_client.make_request(
                    url_name="GET_STREAMS",
                    http_method="GET",
                    query_params={
                        "game_id": category["id"],
                        "first": 100,
                        "after": pagination["cursor"],
                    },
                )
                data = await response_into_dict(response)

                if data:
                    buffer_inserts.append(insert_streams_data(data))
                    counter += 1
            else:
                break

        await asyncio.gather(*buffer_inserts)


async def parse_specific_streams(
    game_id,
    user_id,
    user_login,
    first,
    after,
    before,
    language,
):
    """
    Function to parse stremas by different options.
    """
    twitch_client = await get_twitch_client()

    response = await twitch_client.make_request(
        url_name="GET_STREAMS",
        http_method="GET",
        query_params={
            "game_id": game_id,
            "user_id": user_id,
            "user_login": user_login,
            "first": first,
            "after": after,
            "before": before,
            "language": language,
        },
    )
    data = await response_into_dict(response)
    await insert_streams_data(data)
