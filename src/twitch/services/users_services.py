import asyncio

from src.twitch.repository.streams_repository import get_streams_data
from src.twitch.repository.users_repository import insert_users_data
from src.twitch.utils import divide_chunks, response_into_dict
from src.main import get_twitch_client


async def auto_parse_all_users():
    """
    Function to auto-parse all users info of streams in database.

    Parses users' info by sending requests with chunks of users' ids.
    """
    twitch_client = await get_twitch_client()
    buffer_inserts = []

    streams = await get_streams_data()

    users_ids = [stream["user_id"] for stream in streams]
    chunk = 100
    splited_ids = list(divide_chunks(users_ids, chunk))

    for ids_chunk in splited_ids:
        query_params = [("id", user_id) for user_id in ids_chunk]
        response = await twitch_client.make_request(
            url_name="GET_USER",
            http_method="GET",
            query_params=query_params,
        )
        data = await response_into_dict(response)
        if data:
            buffer_inserts.append(insert_users_data(data))

    await asyncio.gather(*buffer_inserts)


async def parse_specific_user(user_id: str, login: str):
    """
    Function to start parsing user by its user_id or login.
    """
    twitch_client = await get_twitch_client()

    response = await twitch_client.make_request(
        url_name="GET_USER",
        http_method="GET",
        query_params={"id": user_id, "login": login},
    )
    data = await response_into_dict(response)
    await insert_users_data(data)
