from .mongoDb import MongoDb
from ..config import Config


class ConfigDB(MongoDb):
    def __init__(self):
        super().__init__()
        self.col = self.get_collection("configs")

    def new_config(self, key: str, value: str):
        return dict(key=key, value=value)

    async def update_config(self, key, value):
        return await self.col.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)  # type: ignore

    async def get_settings(self, key):
        if key.startswith("SETTINGS_") and not key.startswith("SETTINGS_-100"):
            key = "SETTINGS_PM"
        config = await self.col.find_one({"key": key})  # type: ignore
        if config:
            return config["value"]
        if key.startswith("SETTINGS_"):
            return {
                "AUTO_FILTER": Config.AUTO_FILTER,
                "IMDB": Config.IMDB,
                "IMDB_POSTER": Config.IMDB_POSTER,
                "CHANNEL": Config.CHANNEL,
                "PM_IMDB": Config.PM_IMDB,
                "PM_IMDB_POSTER": Config.PM_IMDB_POSTER,
                "DOWNLOAD_BUTTON": Config.DOWNLOAD_BUTTON,
                "PHOTO_FILTER": Config.PHOTO_FILTER,
                "VIDEO_FILTER": Config.VIDEO_FILTER,
                "SPELL_CHECK": Config.SPELL_CHECK,
                "IS_BUTTON": Config.IS_BUTTON,
                "IS_EPISODES": Config.IS_EPISODES,
                "IS_YEARS": Config.IS_YEARS,
                "IS_SEASONS": Config.IS_SEASONS,
                "IS_QUALITIES": Config.IS_QUALITIE,
                "IS_SENDALL": Config.IS_SENDALL,
                "IS_LANGUAGES": Config.IS_LANGUAGES,
                "AUTO_DELETE": Config.AUTO_DELETE,
 
            }
        return {}


configDB = ConfigDB()
