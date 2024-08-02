
from TechKP.plugins.autofilter import auto_filter
from TechKP.config.config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import Client, filters, enums

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    if Config.PM_SEARCH == True:
        await auto_filter(bot, message)
    else:
        await bot.send_message(chat_id=Config.LOG_CHANNEL, text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>")
