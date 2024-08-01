from typing import Dict, Union, List
from pyrogram.types import ChatMember


class Cache:
    BANNED: List[int] = []
    CANCEL_BROADCAST: bool = False
    ADMINS: Dict[int, Dict[str, Union[List[int], float, Dict[int, ChatMember]]]] = {}
    USERNAMES = {}
    BUTTONS = {}
    BUTTONS2 = {}
    CANCEL = False
    CURRENT = 0
    SEARCH_DATA = {}
    SETTINGS_CACHE = {}
    IMDB_CAP = {}
    IMDB_CAP2 = {}
    ME = None
    U_NAME = None
    B_NAME = None
    B_LINK = None
    CHAT = {}
    BOT = None
    GETALL2 = {}
    GETALL = {}
