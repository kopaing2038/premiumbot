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

async def resolve_listener(client: Client, update: types.Update):
    if isinstance(update, types.CallbackQuery):
        await handle_callback_query(client, update)
    elif isinstance(update, types.InlineQuery):
        await handle_inline_query(client, update)
    elif isinstance(update, types.ChosenInlineResult):
        await handle_chosen_inline_result(client, update)
    elif isinstance(update, types.Message):
        await handle_message(client, update)

async def handle_callback_query(client: Client, callback_query: types.CallbackQuery):
    # Handle callback query here
    LOGGER(__name__).info(f"Received callback query: {callback_query.data}")
    await callback_query.answer("Callback query received!")

async def handle_inline_query(client: Client, inline_query: types.InlineQuery):
    # Handle inline query here
    LOGGER(__name__).info(f"Received inline query: {inline_query.query}")
    results = [types.InlineQueryResultArticle(
        id="1",
        title="Sample Result",
        input_message_content=types.InputTextMessageContent(
            message_text="This is a sample result"
        )
    )]
    await inline_query.answer(results)

async def handle_chosen_inline_result(client: Client, chosen_inline_result: types.ChosenInlineResult):
    # Handle chosen inline result here
    LOGGER(__name__).info(f"Chosen inline result: {chosen_inline_result.result_id}")

async def handle_message(client: Client, message: types.Message):
    # Handle messages here
    LOGGER(__name__).info(f"Received message: {message.text}")
    await message.reply("Message received!")

TechKPBot.add_handler(CallbackQueryHandler(resolve_listener), group=-2)
TechKPBot.add_handler(InlineQueryHandler(resolve_listener), group=-2)
TechKPBot.add_handler(ChosenInlineResultHandler(resolve_listener), group=-2)
TechKPBot.add_handler(MessageHandler(resolve_listener), group=-2)

multi_clients = {}
work_loads = {}
