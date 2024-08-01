from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase, AgnosticCollection

from ..config import Config


DATABASE_URL = Config.DATABASE_URI
SERIES_URL = Config.SERIES_URI
SESSION_NAME = Config.SESSION_NAME

class MongoDb:
    
    def __init__(self):
        self._client = AsyncIOMotorClient(DATABASE_URL)
        self.db : AgnosticDatabase = self._client[SESSION_NAME]

    def get_collection(self, name: str) -> AgnosticCollection:
        return self.db[name]
    

    
class SeriesMongoDb:
    
    def __init__(self):
        self._client = AsyncIOMotorClient(SERIES_URL)
        self.db : AgnosticDatabase = self._client[SESSION_NAME]

    def get_collection(self, name: str) -> AgnosticCollection:
        return self.db[name]



