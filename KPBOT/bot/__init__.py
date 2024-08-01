
import logging
from pyrogram import Client
from pyromod import listen
from TechKP.config.config import Config
from TechKP.utils.cache import Cache
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web
from pyrogram import Client


class TechKPXBot(Client):

    def __init__(self):
        super().__init__(
            name='AutoKPBot',
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            sleep_threshold=5,
            workers=150,
            plugins={"root": "TechKP/plugins"}
        )

    async def set_self(self):
        Cache.BOT = self
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

TechKPBot = TechKPXBot()

multi_clients = {}
work_loads = {}
