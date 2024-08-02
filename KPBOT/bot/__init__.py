import logging
from pyrogram import Client, types, handlers
from pyromod import listen
from TechKP.config.config import Config
from TechKP.utils.cache import Cache
from typing import Union, Optional, AsyncGenerator
from aiohttp import web


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

from pyrogram import Client, types
from pyrogram.handlers import CallbackQueryHandler, InlineQueryHandler, ChosenInlineResultHandler, MessageHandler
from TechKP.utils.logger import LOGGER

async def resolve_listener(
    client: PatchedClient,
    update: Union[types.CallbackQuery, types.Message, types.InlineQuery, types.ChosenInlineResult],
):
    if isinstance(update, types.CallbackQuery):
        if update.message:
            key = f"{update.message.chat.id}:{update.message.id}"
        elif update.inline_message_id:
            key = update.inline_message_id
        else:
            return
    elif isinstance(update, (types.ChosenInlineResult, types.InlineQuery)):
        key = str(update.from_user.id)
    else:
        key = str(update.chat.id)  # type: ignore

    listener = client.listeners.get(key)

    if listener and not listener["future"].done():  # type: ignore
        if callable(listener["filters"]):
            if not await listener["filters"](client, update):
                update.continue_propagation()
        listener["future"].set_result(update)  # type: ignore
        update.stop_propagation()
    else:
        if listener and listener["future"].done():  # type: ignore
            client.remove_listener(key, listener["future"])

TechKPBot.add_handler(CallbackQueryHandler(resolve_listener), group=-2)
TechKPBot.add_handler(InlineQueryHandler(resolve_listener), group=-2)
TechKPBot.add_handler(ChosenInlineResultHandler(resolve_listener), group=-2)
TechKPBot.add_handler(MessageHandler(resolve_listener), group=-2)

multi_clients = {}
work_loads = {}
