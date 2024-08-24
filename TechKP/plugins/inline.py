from TechKP.config.config import Config
from TechKP.database import configDB as config_db
from TechKP.utils.botTools import check_fsub, format_buttons, get_size
import re
import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, 
                            InlineQueryResultCachedDocument, InlineQuery, 
                            CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo)
from TechKP.database.autofilter import a_filter, b_filter
from TechKP.database.db import db


@Client.on_inline_query()
async def answer(bot, query: InlineQuery):
    """Show search results for given inline query."""
    
    user_id = query.from_user.id

    # Check for premium access
    if not await db.has_premium_access(user_id):
        btn = [
            [InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],
            [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url="https://t.me/KOPAINGLAY15")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)

        await bot.send_photo(
            chat_id=user_id,
            photo=Config.PAYMENT_QR,
            caption=Config.PAYMENT_TEXT,
            reply_markup=reply_markup
        )
        await query.answer(results=[], cache_time=0)
        return

    # Process the query
    results = []
    string, file_type = parse_query(query.query)
    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)

    try:
        files, next_offset, total = await a_filter.get_search_results(
            string, file_type=file_type, offset=offset, filter=True, photo=Config.PHOTO_FILTER
        )
    except Exception as e:
        logging.exception(f"Error fetching search results: {str(e)}")
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=0,
            switch_pm_text=f"{emoji.CROSS_MARK} Error fetching results",
            switch_pm_parameter="error"
        )
        return

    # Format the results
    for file in files:
        title = file['file_name']
        size = get_size(file['file_size'])
        results.append(
            InlineQueryResultCachedDocument(
                title=title,
                document_file_id=file['file_id'],
                caption=title,
                description=f"Size: {size}\nType: {file['file_type']}",
                reply_markup=reply_markup
            )
        )

    # Send the results
    switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}" if results else f"{emoji.CROSS_MARK} No results"
    if string:
        switch_pm_text += f' for "{string}"'
    
    try:
        await query.answer(
            results=results,
            is_personal=True,
            cache_time=0,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="start" if results else "okay",
            next_offset=str(next_offset) if results else ""
        )
    except QueryIdInvalid:
        pass  # Handle specific QueryIdInvalid error
    except Exception as e:
        logging.exception(f"Error sending inline query response: {str(e)}")


def parse_query(query):
    """Parse the inline query to extract the search string and file type."""
    if '|' in query:
        string, file_type = query.split('|', maxsplit=1)
        return string.strip(), file_type.strip().lower()
    return query.strip(), None


def get_reply_markup(query):
    """Generate reply markup for search options."""
    buttons = [
        [InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)],
        [InlineKeyboardButton("Mɪɴɪ Aᴘᴘ Sᴇᴀʀᴄʜ", web_app=WebAppInfo(url=Config.MINI_APP_URL))]
    ]
    return InlineKeyboardMarkup(buttons)
