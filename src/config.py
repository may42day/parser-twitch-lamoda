from pydantic import Field, MongoDsn, RedisDsn, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabasebSettings(BaseSettings):
    """
    Configuration for database connections.

    Attributes:
    - mongo_dsn (MongoDsn) - MongoDB data source name.
    - redis_dsn (RedisDsn) - Redis data source name.
    - kafka_bootstrap_servers (str) - Kafka bootstrap server address.
    """

    mongo_dsn: MongoDsn = Field("mongodb://localhost:27017/", env="MONGO_DSN")
    redis_dsn: RedisDsn = Field("redis://localhost", env="REDIS_DSN")
    kafka_bootstrap_servers: str = Field(
        "localhost:9093", env="KAFKA_BOOTSTRAP_SERVERS"
    )


class TwitchCredentials(BaseSettings):
    """
    Configuration for TwitchAPIClient.

    Attributes:
    - twitch_client_id (str) - client ID for Twitch API access.
    - twitch_client_secret (str) - client secret for Twitch API access.
    """

    twitch_client_id: str
    twitch_client_secret: str


class LamodaUrls(BaseSettings):
    """
    Configuration with Lamoda links.

    Attributes:
    - LAMODA_URL_BASE - lamoda base url.
    - LAMODA_URL_MEN_BREADCRUMB - lamoda men category link.
    - LAMODA_URL_WOMEN_BREADCRUMB - lamoda women category link.
    - LAMODA_URL_KIDS_BREADCRUMB - lamoda kids category link.
    """

    LAMODA_URL_BASE: str
    LAMODA_URL_MEN_BREADCRUMB: HttpUrl
    LAMODA_URL_WOMEN_BREADCRUMB: HttpUrl
    LAMODA_URL_KIDS_BREADCRUMB: HttpUrl


class Settings(DatabasebSettings, TwitchCredentials, LamodaUrls):
    """
    Configuration for project.

    Inherits from DatabasebSettings, TwitchCredentials, LamodaUrls.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow", case_sensitive=False
    )


settings = Settings()
