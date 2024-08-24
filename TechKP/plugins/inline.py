from TechKP.config.config import Config
from TechKP.database import configDB as config_db
from TechKP.utils.botTools import (
    check_fsub,
    format_buttons,
    get_size
)
import re
import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from TechKP.database.autofilter import a_filter, b_filter
from TechKP.database.db import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo


@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""

    if not await db.has_premium_access(query.from_user.id):
        btn = [
            [InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],
            [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await bot.send_photo(
            chat_id=query.from_user.id,
            photo=Config.PAYMENT_QR,
            caption=Config.PAYMENT_TEXT,
            reply_markup=reply_markup
        )
        await query.answer(results=[], cache_time=0)
        return
    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)
    files, next_offset, total = await a_filter.get_search_results(
        string, file_type=file_type, offset=offset, filter=True, photo=Config.PHOTO_FILTER
    )

    for file in files:
        title = file['file_name']
        size = get_size(file['file_size'])
        results.append(
            InlineQueryResultCachedDocument(
                title=file['file_name'],
                document_file_id=file['file_id'],
                caption=title,
                description=f"Size: {size}\nType: {file['file_type']}",
                reply_markup=reply_markup)
        )

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
        if string:
            switch_pm_text += f" for {string}"
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=0,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
        except QueryIdInvalid:
            pass
        except Exception as e:
            logging.exception(str(e))
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'

        await query.answer(
            results=[],
            is_personal=True,
            cache_time=0,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="okay"
        )


def get_reply_markup(query):
    buttons = [
        [InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)],
        [InlineKeyboardButton("Mɪɴɪ Aᴘᴘ Sᴇᴀʀᴄʜ", web_app=WebAppInfo(url=Config.MINI_APP_URL))]   
    ]
    return InlineKeyboardMarkup(buttons)
