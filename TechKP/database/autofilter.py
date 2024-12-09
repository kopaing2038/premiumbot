import re

from pymongo.errors import BulkWriteError, DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from ..config import Config
from ..utils.botTools import unpack_new_file_id, parse_link
from ..utils.logger import LOGGER
from .mongoDb import MongoDb, SeriesMongoDb

logger = LOGGER("AUTO_FILTER_DB")

client = AsyncIOMotorClient(Config.DATABASE_URI)
db1 = client[Config.SESSION_NAME]


client2 = AsyncIOMotorClient(Config.SERIES_URI)
db2 = client2[Config.SESSION_NAME]


def check_if_series(file_name: str = "", caption: str = "") -> bool:
    """
    Determines if a file is a part of a series based on its file name or caption.
    
    Args:
        file_name (str): The name of the file to check.
        caption (str): The caption of the media to check (optional).
    
    Returns:
        bool: True if the file is likely a part of a series, False if it's likely a movie.
    """
    # Normalize both file name and caption to lowercase for easier matching
    file_name = file_name.lower() if file_name else ""
    caption = caption.lower() if caption else ""
    
    # Regular expressions to detect common series naming patterns
    series_patterns = [
        r's(\d+)[eex](\d+)',  # Matches patterns like S01E01, s01e01, S1x01, etc.
        r'season[ ._]?(\d+)[ ._]?episode[ ._]?(\d+)',  # Matches patterns like "season 1 episode 1", "season_1_episode_1"
        r'ep[ ._]?(\d+)',  # Matches patterns like "ep1", "ep_01"
        r'(\d+)x(\d+)',  # Matches patterns like "1x01", "10x05"
        r'e(\d+)',  # Matches patterns like "e01"
        r'season[ ._]?(\d+)',  # Matches patterns like "season 01", "season 1"
        r's(\d+)',  # Matches patterns like "s1", "s2"
    ]
    
    # Check if the file name or caption matches any series pattern
    for pattern in series_patterns:
        if re.search(pattern, file_name) or re.search(pattern, caption):
            return True
    
    # If no series patterns are matched, it's likely a movie
    return False


class BaseFilterDb:
    def __init__(self, db_class):
        self.db = db_class()
        self.col = self.db.get_collection(Config.COLLECTION_NAME)  # type: ignore
        self.data = []

    async def insert_many(self, media):
        file = await self.file_dict(media)
        self.data.append(file)
        if len(self.data) >= 200:
            try:
                insert = await self.col.insert_many(self.data, ordered=False)  # type: ignore
            except BulkWriteError as e:
                inserted = e.details["nInserted"]  # type: ignore
            else:
                inserted = len(insert.inserted_ids)
            duplicate = len(self.data) - inserted
            self.data.clear()
            return inserted, duplicate

        logger.info(f'{getattr(media, "file_name", "NO_FILE")} is updated in database')
        return None, None

    async def insert_pending(self):
        try:
            insert = await self.col.insert_many(self.data, ordered=False)  # type: ignore
        except BulkWriteError as e:
            inserted = e.details["nInserted"]  # type: ignore
        else:
            inserted = len(insert.inserted_ids)
        duplicate = len(self.data) - inserted
        self.data.clear()
        return inserted, duplicate

    async def file_dict(self, media):
        file_id, file_ref = unpack_new_file_id(media.file_id)
        if media.file_type == "photo":
            file_ref = media.file_id
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        channel_name = getattr(media, 'channel_name', None)
        file_link = await parse_link(media.chat_id, media.message_id)
        media_id= media.file_unique_id
        return dict(
            _id=media_id,
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            chat_id=media.chat_id,
            channel_name=channel_name,
            file_link=file_link,
            message_id=media.message_id,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )

    async def save_file(self, media):
        """Save file in database"""
        file = await self.file_dict(media)
        try:
            await self.col.insert_one(file)  # type: ignore
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )
            return False, 0
        else:
            logger.info(
                f'{getattr(media, "file_name", "NO_FILE")} is saved to database'
            )
            return True, 1

    async def get_search_results(self, query: str, file_type: str = None, max_results: int = 8, offset: int = 0, filter: bool = False, photo: bool = True):  # type: ignore
        """For given query return (results, next_offset)"""

        query = query.strip()

        if not query:
            raw_pattern = "."
        elif " " not in query:
            raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
        else:
            raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []

        if Config.USE_CAPTION_FILTER:
            filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]}  # type: ignore
        else:
            filter_ = {"file_name": regex}  # type: ignore

        if not photo:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "photo"}}]}

        total_results = await self.col.count_documents(filter_)  # type: ignore
        next_offset = offset + max_results

        if next_offset > total_results:
            next_offset = ""

        cursor = self.col.find(filter_)
        # Sort by recent
        cursor.sort("$natural", -1)  # type: ignore
        # Slice files according to offset and max results
        cursor.skip(offset)  # type: ignore
        cursor.limit(max_results)  # type: ignore
        # Get list of files
        files = await cursor.to_list(length=max_results)

        return files, next_offset, total_results


    async def get_series_search_results(
        self, 
        query: str, 
        file_type: str = None, 
        max_results: int = 8, 
        offset: int = 0, 
        filter: bool = False, 
        photo: bool = True
    ):  
        """For a given query return (results, next_offset)"""

        query = query.strip()

        if not query:
            raw_pattern = "."
        elif " " not in query:
            raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
        else:
            raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []

        if Config.USE_CAPTION_FILTER:
            filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]}  # type: ignore
        else:
            filter_ = {"file_name": regex}  # type: ignore

        if not photo:
            filter_ = {"$and": [filter_, {"file_type": {"$ne": "photo"}}]}

        total_results = await self.col.count_documents(filter_)  # type: ignore
        next_offset = offset + max_results

        if next_offset > total_results:
            next_offset = ""

        cursor = self.col.find(filter_)
        # Sort by recent
        cursor.sort("$natural", -1)  # type: ignore
        # Slice files according to offset and max results
        cursor.skip(offset)  # type: ignore
        cursor.limit(max_results)  # type: ignore
        # Get list of files
        files = await cursor.to_list(length=max_results)

        # Filter results to only include series
        series_files = []
        for file in files:
            file_name = file.get("file_name", "")
            caption = file.get("caption", "")
            if check_if_series(file_name, caption):
                series_files.append(file)

        return series_files, next_offset, total_results



    async def get_file_details(self, file_id: str):
        return await self.col.find_one({"file_id": file_id})  # type: ignore

    async def get_bad_files(self, query: str, file_type: str = None, offset: int = 0, filter: bool = False):
        query = query.strip()
        if not query:
            raw_pattern = '.'
        elif ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            return []

        if Config.USE_CAPTION_FILTER:
            filter_ = {"$or": [{"file_name": regex}, {"caption": regex}]}  # type: ignore
        else:
            filter_ = {"file_name": regex}  # type: ignore

        if file_type:
            filter_["file_type"] = file_type

        total_results = await self.col.count_documents(filter_)  # type: ignore
        cursor = self.col.find(filter_)
        cursor.sort('$natural', -1)
        files = await cursor.to_list(length=total_results)
        return files, total_results

class FiltersDb(BaseFilterDb):
    def __init__(self):
        super().__init__(MongoDb)


class FiltersDb2(BaseFilterDb):
    def __init__(self):
        super().__init__(SeriesMongoDb)


a_filter = FiltersDb()
b_filter = FiltersDb2()
