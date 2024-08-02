import asyncio
import re
from pyrogram import enums, filters, types
from pyrogram.errors import (ChannelInvalid, UsernameInvalid,
                             UsernameNotModified)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import types, enums, filters, Client
from ..config import Config
from ..database import a_filter, b_filter
from ..utils.cache import Cache
from ..utils.logger import LOGGER
import re, time, datetime
from ..utils.botTools import get_readable_time
logger = LOGGER("INDEX")


lock = asyncio.Lock()
_REGEX = r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"


@Client.on_message(filters.private & filters.command('index'))
async def send_for_index(bot, message):
    vj = await bot.ask(message.chat.id, "**Now Send Me Your Channel Last Post Link Or Forward A Last Message From Your Index Channel.**")
    if vj.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(vj.text)
        if not match:
            return await vj.reply('Invalid link\n\nTry again by /index')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif vj.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = vj.forward_from_message_id
        chat_id = vj.forward_from_chat.username or vj.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await vj.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await vj.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await vj.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and iam not a admin of the group.')

    if message.from_user.id in Config.ADMINS:
        buttons = [
            [
                InlineKeyboardButton(
                    "Yes",
                    callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "Series Only Yes",
                    callback_data=f"seriesindex#accept#{chat_id}#{last_msg_id}#{message.from_user.id}",
                )
            ],
            [
                InlineKeyboardButton("close", callback_data="close_data"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f"Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>",
            reply_markup=reply_markup,
        )


@Client.on_message(filters.command("setskip") & filters.user(Config.ADMINS))  # type: ignore
async def set_skip_number(bot: Client, message: types.Message):
    if " " in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        Cache.CURRENT = int(skip)  # type: ignore
    else:
        await message.reply("Give me a skip number")


async def index_files_to_db(lst_msg_id: int, chat: int, msg: types.Message, bot: Client):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    start_time = time.time()
    fetched = 0
    remaining = lst_msg_id - Cache.CURRENT
    current = Cache.CURRENT
    
    async with lock:
        try:
            Cache.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, Cache.CURRENT):  # type: ignore
                if Cache.CANCEL:
                    time_taken = get_readable_time(time.time() - start_time)
                    inserted, errored = await a_filter.insert_pending()
                    if inserted:
                        total_files += inserted
                    if errored:
                        duplicate += errored
                    await msg.edit(
                        f"Time Taken: <code>{time_taken}</code>\nSuccessfully Cancelled!!\n\nSaved <code>{total_files} / {current}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
                    )
                    break
                
                current += 1
                fetched += 1
                remaining -= 1
                
                try:
                    speed = fetched / (time.time() - start_time)
                    eta = remaining / speed
                except ZeroDivisionError:
                    speed = 0
                    eta = 0

                if current % 200 == 0:
                    can = [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nRemaining Messages: <code>{remaining}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>\n\nETA: <code>{get_readable_time(eta)}</code>",
                        reply_markup=reply,
                    )
                
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT,
                    enums.MessageMediaType.PHOTO
                ]:
                    unsupported += 1
                    continue
                
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                
                if message.media == enums.MessageMediaType.PHOTO:
                    media.file_type = "photo"
                    media.file_name = message.caption.split('\n')[0] if message.caption else ""
                    media.mime_type = "image/jpg"
                elif message.media == enums.MessageMediaType.VIDEO:
                    media.file_type = "video"
                    media.file_name = message.video.file_name if message.caption else ""
                    media.mime_type = "video/mp4"
                elif message.media == enums.MessageMediaType.AUDIO:
                    media.file_type = "audio"
                    media.file_name = message.audio.file_name if message.caption else ""
                    media.mime_type = message.audio.mime_type if message.audio.mime_type else "audio/mpeg"
                elif message.media == enums.MessageMediaType.DOCUMENT and message.document is not None:
                    media.file_type = "document"
                    media.file_name = message.document.file_name if message.document.file_name else ""
                    media.mime_type = message.document.mime_type if message.document.mime_type else ""
                
                media.caption = message.caption if message.caption else ""
                media.chat_id = message.chat.id
                media.channel_name = message.chat.username or message.chat.title
                media.message_id = message.id
                
                inserted, errored = await a_filter.insert_many(media)
                if inserted:
                    total_files += inserted
                if errored:
                    duplicate += errored

        except Exception as e:
            logger.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            time_taken = get_readable_time(time.time() - start_time)
            inserted, errored = await a_filter.insert_pending()
            if inserted:
                total_files += inserted
            if errored:
                duplicate += errored
            await msg.edit(
                f"Time Taken: <code>{time_taken}</code>\n\nSuccessfully saved <code>{total_files} / {current}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
            )


async def series_index_files_to_db(lst_msg_id: int, chat: int, msg: types.Message, bot: Client):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    start_time = time.time()
    fetched = 0
    remaining = lst_msg_id - Cache.CURRENT
    current = Cache.CURRENT
    
    async with lock:
        try:
            Cache.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, Cache.CURRENT):  # type: ignore
                if Cache.CANCEL:
                    time_taken = get_readable_time(time.time() - start_time)
                    inserted, errored = await b_filter.insert_pending()
                    if inserted:
                        total_files += inserted
                    if errored:
                        duplicate += errored
                    await msg.edit(
                        f"Time Taken: <code>{time_taken}</code>\nSuccessfully Cancelled!!\n\nSaved <code>{total_files} / {current}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
                    )
                    break
                
                current += 1
                fetched += 1
                remaining -= 1
                
                try:
                    speed = fetched / (time.time() - start_time)
                    eta = remaining / speed
                except ZeroDivisionError:
                    speed = 0
                    eta = 0

                if current % 200 == 0:
                    can = [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nRemaining Messages: <code>{remaining}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>\n\nETA: <code>{get_readable_time(eta)}</code>",
                        reply_markup=reply,
                    )
                
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT,
                    enums.MessageMediaType.PHOTO
                ]:
                    unsupported += 1
                    continue
                
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                
                if message.media == enums.MessageMediaType.PHOTO:
                    media.file_type = "photo"
                    media.file_name = message.caption.split('\n')[0] if message.caption else ""
                    media.mime_type = "image/jpg"
                elif message.media == enums.MessageMediaType.VIDEO:
                    media.file_type = "video"
                    media.file_name = message.video.file_name if message.caption else ""
                    media.mime_type = "video/mp4"
                elif message.media == enums.MessageMediaType.AUDIO:
                    media.file_type = "audio"
                    media.file_name = message.audio.file_name if message.caption else ""
                    media.mime_type = message.audio.mime_type if message.audio.mime_type else "audio/mpeg"
                elif message.media == enums.MessageMediaType.DOCUMENT and message.document is not None:
                    media.file_type = "document"
                    media.file_name = message.document.file_name if message.document.file_name else ""
                    media.mime_type = message.document.mime_type if message.document.mime_type else ""
                
                media.caption = message.caption if message.caption else ""
                media.chat_id = message.chat.id
                media.channel_name = message.chat.username or message.chat.title
                media.message_id = message.id
                
                inserted, errored = await b_filter.insert_many(media)
                if inserted:
                    total_files += inserted
                if errored:
                    duplicate += errored

        except Exception as e:
            logger.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            time_taken = get_readable_time(time.time() - start_time)
            inserted, errored = await b_filter.insert_pending()
            if inserted:
                total_files += inserted
            if errored:
                duplicate += errored
            await msg.edit(
                f"Time Taken: <code>{time_taken}</code>\n\nSuccessfully saved <code>{total_files} / {current}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>"
            )

#
