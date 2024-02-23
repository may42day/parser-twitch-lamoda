import asyncio
from typing import Dict, List, Union
import httpx
from datetime import datetime, timedelta


TWITCH_URLS = {
    "OAUTH2": "https://id.twitch.tv/oauth2/token",
    "VALIDATE_TOKEN": "https://id.twitch.tv/oauth2/validate",
    "GET_TOP_GAMES": "https://api.twitch.tv/helix/games/top",
    "GET_GAMES": "https://api.twitch.tv/helix/games",
    "GET_STREAMS": "https://api.twitch.tv/helix/streams",
    "GET_USER": "https://api.twitch.tv/helix/users",
}

client = httpx.AsyncClient()
timeout = httpx.Timeout(connect=20.0, read=20.0, write=10.0, pool=10.0)

TWITCH_CLIENT_HTTP_METHODS = {
    "GET": client.get,
    "POST": client.post,
}


class TwitchAPIClient:
    """
    Twitch API Client to make requests to Twitch APIs.
    Provides with auth, refreshing token and making requests.

    Public methods:
        - make_request - making request with specific url

    Protected methods:
        - is_token_expired - checking whether token is expired.
        - prepare_headers - creates dict with necessary headers params.
        - refresh_token - gets new access token.

    Attributes:
        - client_id (str) - app's registered client ID.
        - client_secret (str) - app's registered client secret.
        - urls (dict) - dict of url names and links related to it.
        - http_methods (dict) - dict of http methods and its functions from requests lib.
        - access_token (str) - access token for making requests.
        - token_expires_at (datetime) - datetime represents token expiration.
    """

    def __init__(self, client_id, client_secret):
        """
        Args:
            - client_id (str, required) - app's registered client ID.
            - client_secret (str, required) - app's registered client secret.
        """
        self.client_id = client_id
        self.client_secret = client_secret

        self.urls = TWITCH_URLS
        self.http_methods = TWITCH_CLIENT_HTTP_METHODS

        self.access_token = None
        self.token_expires_at = None

    async def make_request(
        self, url_name: str, http_method: str, query_params: dict = {}, body: dict = {}
    ) -> dict:
        """
        Function to make request to twitch API.

        Checks whether token is valid and then makes request.
        Repeat request if there is unauthorized status code.

        Args:
            - url_name (str, required) - url name.
            - http_method (str, required) - http method name.
            - query_params (dict, optional) - - data represents request's query params.
            - body (dict, optional) - data represents request's body.
        """

        if not self.access_token or await self._is_token_expired():
            await self._refresh_token()

        if url_name not in self.urls:
            raise ValueError("Unsupported URL name.")
        if http_method not in self.http_methods:
            raise ValueError("Unsupported HTTP method.")

        url = self.urls[url_name]
        headers = await self._prepare_headers()
        handler = self.http_methods[http_method]
        params = await self.prepare_query_params(query_params)

        retries = 0
        max_retries = 3
        while retries < max_retries:
            try:
                response = await handler(url, headers=headers, params=params)
                break
            except httpx.ConnectTimeout:
                retries += 1

        if response.status_code == 401:
            await self._refresh_token()
            response = await handler(url, headers=headers, params=params)

        return response

    async def prepare_query_params(
        self, query_params: Union[List, Dict]
    ) -> Union[List, Dict]:
        """
        Function to delete params with nullable value.
        """
        if isinstance(query_params, list):
            return query_params

        params = {}
        for param in query_params:
            if query_params[param]:
                params[param] = query_params[param]
        return params

    async def _refresh_token(self):
        """
        Function to get new token.

        Sends POST request to twitch OAuth2 service with credentials to get new token.
        Updates APIClient statement with new token and time of its expiration if success request.
        Otherwise retries to get new token in 1 sec.

        Request data:
        - client_id (str, required) - app's registered client ID.
        - client_secret (str, required) - app's registered client secret.
        - grant_type (str, required) - must be set to client_credentials.
        """

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = await httpx.AsyncClient().post(self.urls["OAUTH2"], data=data)
        if response.status_code == 200:
            response_data = response.json()
            self.access_token = response_data["access_token"]
            expires_in_sec = response_data["expires_in"]
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in_sec)
        elif response.status_code == 400:
            raise ValueError(
                "Invalid credentials: client_id or client_secret.Must be set in environment"
            )
        else:
            await asyncio.sleep(1)
            await self._refresh_token()

    async def _is_token_expired(self):
        """
        Function to check whether access token is expired.
        """

        if self.token_expires_at:
            now = datetime.now()
            return self.token_expires_at < now
        return True

    async def _prepare_headers(self) -> dict:
        """
        Function to create dict with params which represents request's headers.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.client_id,
        }

        return headers
