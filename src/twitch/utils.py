from datetime import datetime


async def response_into_dict(response) -> dict:
    """
    Function to convert TwitchAPIClient response to dict or retunr None if it's empty.
    """
    data = response.json().get("data")
    if data and data != "null":
        return response.json().get("data")
    return None


async def add_current_time(data):
    """
    Function to add current time (created_at) to instances
    """
    current_time = datetime.now().isoformat()
    for item in data:
        item["created_at"] = current_time

    return data


def divide_chunks(l, n):
    """
    Generator to split list into chunks of specific length.
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]
