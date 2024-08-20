
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
    caption = message.caption or 'No Caption'  # Use message.caption for captions

    # Ensure content is not None
    if content is None:
        content = ""

    if content.startswith("/") or content.startswith("#"): 
        return  # Ignore commands and hashtags

    if user_id in Config.ADMINS: 

        return
    #await message.forward(chat_id=Config.ADMINS[0])
    # Check for media files and process them
    if message.photo:
        await bot.send_photo(
            chat_id=Config.LOG_CHANNEL,
            photo=message.photo.file_id,
            caption=f"<b>#𝐏𝐌_𝐏𝐇𝐓\n\nNᴀᴍᴇ : {mention} \n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {caption}</b>"
        )
        for admin in Config.ADMINS:
            await bot.send_photo(
                chat_id=admin,
                photo=message.photo.file_id,
                caption=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : {caption}"
            )

    elif message.video:
        await bot.send_video(
            chat_id=Config.LOG_CHANNEL,
            video=message.video.file_id,
            caption=f"<b>#𝐏𝐌_𝐕𝐃𝐎\n\nNᴀᴍᴇ : {mention} \n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {caption}</b>"
        )
        for admin in Config.ADMINS:
            await bot.send_video(
                chat_id=admin,
                video=message.video.file_id,
                caption=f"User Name : {mention}\nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : {caption}"
            )

    elif message.audio:
        await bot.send_audio(
            chat_id=Config.LOG_CHANNEL,
            audio=message.audio.file_id,
            caption=f"<b>#𝐏𝐌_𝐀𝐔𝐃𝐈𝐎\n\nNᴀᴍᴇ : {mention} \n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {caption}</b>"
        )
        for admin in Config.ADMINS:
            await bot.send_audio(
                chat_id=admin,
                audio=message.audio.file_id,
                caption=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : {caption}"
            )

    elif message.document:
        await bot.send_document(
            chat_id=Config.LOG_CHANNEL,
            document=message.document.file_id,
            caption=f"<b>#𝐏𝐌_𝐃𝐎𝐂\n\nNᴀᴍᴇ : {mention} \n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {caption}</b>"
        )
        for admin in Config.ADMINS:
            await bot.send_document(
                chat_id=admin,
                document=message.document.file_id,
                caption=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : {caption}"
            )

    else:
        if Config.PM_SEARCH == True:
            await auto_filter(bot, message, pm_mode=True)

        await bot.send_message(
            chat_id=Config.LOG_CHANNEL,
            text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {mention}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : <code>{content}</code></b>"
        )
        for admin in Config.ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=f"User Name : {mention} \nUser ID : <code>{user_id}</code>\nMᴇssᴀɢᴇ : <code>{content}</code>"
            )


