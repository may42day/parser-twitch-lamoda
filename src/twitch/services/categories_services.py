import asyncio

from src.twitch.repository.categories_repository import insert_categories_data
from src.twitch.utils import response_into_dict
from src.main import get_twitch_client


async def auto_parse_all_categories():
    """
    Function to auto-parse all games(categories).

    Makes requests with incremental page untill no categories returns.
    """
    buffer_inserts = []
    twitch_client = await get_twitch_client()

    response = await twitch_client.make_request(
        url_name="GET_TOP_GAMES",
        http_method="GET",
        query_params={"first": 100},
    )
    data = await response_into_dict(response)
    if data:
        buffer_inserts.append(insert_categories_data(data))

        while True:
            pagination = response.json().get("pagination")
            if pagination:
                response = await twitch_client.make_request(
                    url_name="GET_TOP_GAMES",
                    http_method="GET",
                    query_params={"first": 100, "after": pagination["cursor"]},
                )
                data = await response_into_dict(response)
                buffer_inserts.append(insert_categories_data(data))
            else:
                break

        await asyncio.gather(*buffer_inserts)


async def parse_top_categories(first: int, after: str, before: str):
    """
    Function to parse top categories.

    Args:
    - after (str, optional) - pagination param used to get the next page of results.
    - before (str, optional) - pagination param used to get the previous page of results.
    - first (int, optional, max 100) - the maximum number of items to return per page in the response.
    """
    twitch_client = await get_twitch_client()

    response = await twitch_client.make_request(
        url_name="GET_TOP_GAMES",
        http_method="GET",
        query_params={"first": first, "after": after, "before": before},
    )

    data = await response_into_dict(response)
    if data:
        inserted_ids = await insert_categories_data(data)
        return {"inserted_ids": inserted_ids}


async def parse_category(id: int, name: int, igdb_id: int):
    """
    Function to parse specific category by options.

    Args:
    - id (str) - category id.
    - name (str) - category name.
    - igdb_id (int) - id represents IGDB id.
    """
    twitch_client = await get_twitch_client()

    response = await twitch_client.make_request(
        url_name="GET_GAMES",
        http_method="GET",
        query_params={"id": id, "name": name, "igdb_id": igdb_id},
    )
    data = await response_into_dict(response)
    if data:
        inserted_ids = await insert_categories_data(data)
        return {"inserted_ids": inserted_ids}
