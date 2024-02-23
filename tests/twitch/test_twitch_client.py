from datetime import datetime, timedelta
import pytest

from src.twitch.client import TwitchAPIClient
from src.config import settings


@pytest.fixture
def client():
    return TwitchAPIClient(client_id="some_id", client_secret="some_secret")


@pytest.fixture
def client_with_token(client):
    client.access_token = "some_token"
    time_expiration = datetime.now() + timedelta(days=10)
    client.token_expires_at = time_expiration
    return client


class TestTwitchAPIClient:
    """
    Tests Twitch API Client
    """

    def test_unsupported_url_name(self, client_with_token):
        """
        Checking whether invalid url_name is raising error.
        """
        with pytest.raises(ValueError, match="Unsupported URL name."):
            client_with_token.make_request(url_name="invalid_name", http_method="GET")

    def test_unsupported_http_method(self, client_with_token):
        """
        Checking whether invalid http_method is raising error.
        """
        with pytest.raises(ValueError, match="Unsupported HTTP method."):
            client_with_token.make_request(url_name="OAUTH2", http_method="invalid")

    def test_successful_request(self):
        """
        Checking whether request is completed.
        """
        client = TwitchAPIClient(
            client_id=settings.twitch_client_id,
            client_secret=settings.twitch_client_secret,
        )
        response = client.make_request(url_name="GET_TOP_GAMES", http_method="GET")

        assert response.status_code == 200
        assert "data" in response.json()
