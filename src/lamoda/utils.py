from datetime import datetime
from typing import Dict, List, Union
import httpx


async def get_html_text(url, page=None):
    """
    Function to get html page of specific requests.

    Includes pagination of page argument is specified.
    """
    async with httpx.AsyncClient() as client:
        if page:
            repsponse = await client.get(url + f"?page={page}")
        else:
            repsponse = await client.get(url)
        repsponse.raise_for_status()
        return repsponse.text


async def add_current_time(data):
    """
    Function to add current time (created_at) to instances
    """
    current_time = datetime.now().isoformat()
    if isinstance(data, list):
        for item in data:
            item["created_at"] = current_time
    elif isinstance(data, dict):
        data["created_at"] = current_time

    return data


async def prepare_response_data(
    data: Union[List[Dict], Dict]
) -> Union[List[Dict], Dict]:
    """
    Recursive function to prepare data before sending response.

    Replace ObjectId to str value.
    """
    if isinstance(data, list):
        for item in data:
            await prepare_response_data(item)

    elif isinstance(data, dict):
        data["_id"] = str(data["_id"])

        if data.get("categories"):
            await prepare_response_data(data.get("categories"))
        if data.get("products"):
            await prepare_response_data(data.get("products"))
