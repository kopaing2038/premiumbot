
from TechKP.plugins.autofilter import auto_filter
from TechKP.config.config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import Client, filters, enums, types


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    mention = message.from_user.mention
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    if Config.PM_SEARCH == True:
        await auto_filter(bot, message, pm_mode=True)
        await bot.send_message(chat_id=Config.LOG_CHANNEL, text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>")
        for admin in Config.ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : <code>{content}</code>"
            )

    else:
        await bot.send_message(chat_id=Config.LOG_CHANNEL, text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>")

        for admin in Config.ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : <code>{content}</code>"
            )


