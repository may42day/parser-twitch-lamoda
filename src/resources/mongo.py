from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings


client = AsyncIOMotorClient(str(settings.mongo_dsn))

db = client.parsers

# MongoDB collection for Twitch parser instances
db_twitch = db.twitch_collection

# MongoDB collection for Lamoda parser instances
db_lamoda = db.lamoda
