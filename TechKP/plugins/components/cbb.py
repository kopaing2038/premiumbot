import logging, asyncio, time, pytz, re, os, math, random
import json
import pyrogram
from pyrogram import errors, filters, types, Client, enums
from ...database import configDB as config_db
from ...utils.botTools import CONFIGURABLE, get_bool, get_buttons
from TechKP.config.Script import script
from ...utils.cache import Cache
from ...utils.logger import LOGGER
from ...config import Config
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from TechKP.database.db import db 
from ...utils.botTools import (
    check_fsub,
    format_buttons,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
    check_verification,
    get_status,
    handle_next_back
)
from imdb import Cinemagoer 

ia = Cinemagoer()




import asyncio
import re
from pyrogram import enums, filters, types
from pyrogram.errors import (ChannelInvalid, UsernameInvalid,
                             UsernameNotModified)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import types, enums, filters, Client
from ...config import Config
from ...database import a_filter, b_filter
from ...utils.cache import Cache
from ...utils.logger import LOGGER
import re, time, datetime
from ...utils.botTools import get_readable_time
logger = LOGGER("INDEX")


lock = asyncio.Lock()
_REGEX = r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"


@Client.on_callback_query(filters.regex(r"^index"))  # type: ignore
async def index_files(bot: Client, query: types.CallbackQuery):
    if query.data.startswith("index_cancel"):  # type: ignore
        Cache.CANCEL = True  # type: ignore
        return await query.answer("Cancelling Indexing")
    _, sts, chat, lst_msg_id, from_user = query.data.split("#")  # type: ignore
    if sts == "reject":
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been declined by our moderators.",
            reply_to_message_id=int(lst_msg_id),
        )
        return

    if lock.locked():
        return await query.answer("Wait until previous process complete.", show_alert=True)
    msg = query.message

    await query.answer("Processing...⏳", show_alert=True)

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
        ),
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)  # type: ignore

@Client.on_callback_query(filters.regex(r"^seriesindex"))  # type: ignore
async def series_index_files(bot: Client, query: types.CallbackQuery):
    if query.data.startswith("seriesindex_cancel"):  # type: ignore
        Cache.CANCEL = True  # type: ignore
        return await query.answer("Cancelling Indexing")
    _, sts, chat, lst_msg_id, from_user = query.data.split("#")  # type: ignore
    if sts == "reject":
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been declined by our moderators.",
            reply_to_message_id=int(lst_msg_id),
        )
        return

    if lock.locked():
        return await query.answer("Wait until previous process complete.", show_alert=True)
    msg = query.message

    await query.answer("Processing...⏳", show_alert=True)

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="seriesindex_cancel")]]
        ),
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await series_index_files_to_db(int(lst_msg_id), chat, msg, bot)  # type: ignore


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
@Client.on_message(filters.command("gsettings") & filters.user(Config.ADMINS))  # type: ignore
async def handle_settings(bot: Client, msg: types.Message):
    if msg.chat.type == enums.ChatType.PRIVATE:
        settings = await config_db.get_settings(f"SETTINGS_PM")
    else:
        settings = await config_db.get_settings(f"SETTINGS_{msg.chat.id}")

    await msg.reply(
        "Configure your bot here", reply_markup=types.InlineKeyboardMarkup(get_buttons(settings))  # type: ignore
    )


@Client.on_callback_query(filters.regex("^settings"))  # type: ignore
async def setup_settings(bot: Client, query: types.CallbackQuery):
    if query.from_user.id not in Config.ADMINS:
        return await query.answer("This is not for you!")
    set_type, key = query.data.split("#")  # type: ignore
    if set_type == "settings_info":
        return await query.answer(CONFIGURABLE[key]["help"], show_alert=True)  # type: ignore

    # setattr(Config, key, get_bool(getattr(Config, key)))
    if query.message.chat.type == enums.ChatType.PRIVATE:
        data_key = "SETTINGS_PM"
    else:
        data_key = f"SETTINGS_{query.message.chat.id}"
    settings = await config_db.get_settings(data_key)
    settings[key] = get_bool(settings.get(key, True))  # type: ignore
    # setattr(Config, key, settings[key])

    await config_db.update_config(data_key, settings)
    await query.answer()
    try:
        await query.edit_message_reply_markup(types.InlineKeyboardMarkup(get_buttons(settings)))  # type: ignore
    except errors.MessageNotModified:
        pass  # You might want to handle this exception if needed


@Client.on_callback_query(filters.regex(r"^free_users_next"))
async def free_users_next_page(client, query):
    _, offset = query.data.split("#")
    offset = int(offset)
    users, n_offset, total, max_btn = await handle_next_back(await db.get_all_users(), offset=offset, max_results=30)
    b_offset = offset - max_btn

    if n_offset == 0:
        btn = [[
            InlineKeyboardButton("Back", callback_data=f"free_users_next#{b_offset}"),
            InlineKeyboardButton(f"Page {math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar")
        ]]
    elif offset == 0:
        btn = [[
            InlineKeyboardButton(f"Page {math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar"),
            InlineKeyboardButton("Next", callback_data=f"free_users_next#{n_offset}")
        ]]
    else:
        btn = [[
            InlineKeyboardButton("Back", callback_data=f"free_users_next#{b_offset}"),
            InlineKeyboardButton(f"{math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar"),
            InlineKeyboardButton("Next", callback_data=f"free_users_next#{n_offset}")
        ]]

    text = ""
    for user_num, user in enumerate(users, start=offset+1):
        try:
            user_info = await client.get_users([user['id']])
            text += f"{user_num}. <a href='tg://user?id={user['id']}'>{user_info[0].mention}</a> [<code>{user['id']}</code>]\n\n"
        except (PeerIdInvalid, ChannelInvalid, BadRequest) as e:
            logging.warning(f"Invalid user ID: {user['id']} - Error: {str(e)}")
            text += f"{user_num}. <code>{user['id']}</code> (Invalid ID)\n\n"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^premium_next"))
async def premium_users_dbnext_page(client, query):
    _, offset = query.data.split("#")
    offset = int(offset)
    users, n_offset, total, max_btn = await handle_next_back(await db.get_premium_users(), offset=offset, max_results=30)
    b_offset = offset - max_btn

    if n_offset == 0:
        btn = [[
            InlineKeyboardButton("Back", callback_data=f"premium_next#{b_offset}"),
            InlineKeyboardButton(f"Page {math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar")
        ]]
    elif offset == 0:
        btn = [[
            InlineKeyboardButton(f"Page {math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar"),
            InlineKeyboardButton("Next", callback_data=f"premium_next#{n_offset}")
        ]]
    else:
        btn = [[
            InlineKeyboardButton("Back", callback_data=f"premium_next#{b_offset}"),
            InlineKeyboardButton(f"{math.ceil(offset / max_btn) + 1} / {math.ceil(total / max_btn)}", callback_data="bar"),
            InlineKeyboardButton("Next", callback_data=f"premium_next#{n_offset}")
        ]]

    text = ""
    for user_num, user in enumerate(users, start=offset+1):
        try:
            user_info = await client.get_users(user['_id'])
            text += f"{user_num}. <a href='tg://user?id={user['_id']}'>{user_info.mention}</a> [<code>{user['_id']}</code>]\n\n"
        except PeerIdInvalid:
            logging.warning(f"Invalid user ID: {user['_id']}")
            text += f"{user_num}. <code>{user['_id']}</code> (Invalid ID)\n\n"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btn))



@Client.on_callback_query()
async def csdb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT, show_alert=True)
        await query.answer("ᴛʜᴀɴᴋs ꜰᴏʀ ᴄʟᴏsᴇ 🙈")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    elif query.data == "buttons":
        await query.answer("ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 😊", show_alert=True)
    elif query.data == "pages":
        await query.answer("ᴛʜɪs ɪs ᴘᴀɢᴇs ʙᴜᴛᴛᴏɴ 😅")

    elif query.data == "popularmovies":
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='start'),
        ]]
        popular_movies = ia.get_popular100_movies()[:25]
        response_text = "<b>Top 25 Popular Movies:</b>\n\n"
        for idx, movie in enumerate(popular_movies, start=1):
            title = movie.get('title')
            response_text += f"{idx}. {title}\n"
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=response_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )

    elif query.data == "popmovie":
        popular_movies = ia.get_popular100_movies()[:25]
        response_text = "<b>Top 25 Popular Movies:</b>\n\n"
        for idx, movie in enumerate(popular_movies, start=1):
            title = movie.get('title')
            response_text += f"{idx}. {title}\n"
            await query.message.edit_text(
                text=response_text,
                parse_mode=enums.ParseMode.HTML
            )


    elif query.data == "start":
        buttons = [[
            types.InlineKeyboardButton('🔖 Join Our Group to Use Me', url="https://t.me/MKS_RequestGroup")
        ],[
            types.InlineKeyboardButton('⚙ ꜰᴇᴀᴛᴜʀᴇs', callback_data='features'),
            types.InlineKeyboardButton('🎗️ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='premium'),
        ],[
            types.InlineKeyboardButton('Iɴʟɪɴᴇ Sᴇᴀʀᴄʜ ☌', switch_inline_query_current_chat=''),
            types.InlineKeyboardButton('✇ Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs ✇', callback_data='popularmovies')
        ],[
            types.InlineKeyboardButton('⌬ Mᴏᴠɪᴇ Gʀᴏᴜᴘ', url=Config.GROUPS_LINK),
            types.InlineKeyboardButton('✇ Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ ✇', url=Config.CHANNEL_LINK)
        ],[
            types.InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
            types.InlineKeyboardButton('🫠 ᴀʙᴏᴜᴛ 🚩', callback_data='about')
        ],[
            types.InlineKeyboardButton('🤞🏻 ʙᴏᴛ ᴏᴡɴᴇʀ 🤡', callback_data='admin')
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)            
        await query.edit_message_media(
            media=types.InputMediaPhoto(
                media=random.choice(Config.START_IMG),
                caption=script.START_TXT.format(query.from_user.mention, get_status(), query.from_user.id)
            ),
            reply_markup=reply_markup
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('Sᴏᴜʀᴄᴇ Cᴏᴅᴇ', url="https://t.me/KOPAINGLAY15")
        ],[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OWNER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TEXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "premium":
        userid = query.from_user.id
        await query.message.edit(script.PREMIUM_TEXT , reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton('🤞🏻 ʟᴏᴡ ᴘʀɪᴄᴇ ᴘʟᴀɴs 🍿', callback_data='plans')],
        [InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='start')]
        ]))

    elif query.data == "plans":
        userid = query.from_user.id
        await query.edit_message_media(
            media=types.InputMediaPhoto(
                media=random.choice(Config.START_IMG),
                caption=script.PLAN_TEXT
            ),
            reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton('🤞🏻 ʙᴜʏ ᴘʟᴀɴ 🍿', callback_data='buy_plan')],
        [InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='premium')]
        ]))

    elif query.data == "buy_plan":
        userid = query.from_user.id
        await query.edit_message_media(
            media=types.InputMediaPhoto(
                media=Config.PAYMENT_QR,
                caption=script.BUY_PLAN.format(Cache.B_LINK)
            ),
            reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='plans')]
        ]))

    elif query.data == "features":
        buttons = [[
            InlineKeyboardButton('📸 ᴛ-ɢʀᴀᴘʜ', callback_data='telegraph'),
            InlineKeyboardButton('🆎️ ғᴏɴᴛ', callback_data='font')    
        ],[ 
            InlineKeyboardButton('ᴜsᴇʀ ᴄᴍᴅ', callback_data='usercmd'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴍᴅ', callback_data='extra'),
        ],[ 
	    InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='start')
        ]] 
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(                     
            text=script.HELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴍᴅ', callback_data='admincmd'),
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='features')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "admincmd":
        #if user isnt admin then return
        if not query.from_user.id in Config.ADMINS:
            return await query.answer('This Feature Is Only For Admins !' , show_alert=True)
        buttons = [
            [InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='features')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_CMD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data == "usercmd":
        buttons = [
            [InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='features')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USER_CMD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data == 'about':
        await query.message.edit_text(
            script.ABOUT_TEXT.format(query.from_user.mention(),Cache.B_LINK),
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton('⋞ ʜᴏᴍᴇ', callback_data='start')]]
                ),
            disable_web_page_preview = True
        )

    elif query.data == "telegraph":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='features')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)  
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "font":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='features')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons) 
        await query.message.edit_text(
            text=script.FONT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)
  

    elif query.data.startswith("show_options"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            types.InlineKeyboardButton("✅️ ᴀᴄᴄᴇᴘᴛ ᴛʜɪꜱ ʀᴇǫᴜᴇꜱᴛ ✅️", callback_data=f"accept#{user_id}#{msg_id}")
        ],[
            types.InlineKeyboardButton("🚫 ʀᴇᴊᴇᴄᴛ ᴛʜɪꜱ ʀᴇǫᴜᴇꜱᴛ 🚫", callback_data=f"reject#{user_id}#{msg_id}")
        ]]
        try:
            st = await client.get_chat_member(chnl_id, userid)
            if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
                await query.message.edit_reply_markup(types.InlineKeyboardMarkup(buttons))
            elif st.status == enums.ChatMemberStatus.MEMBER:
                await query.answer(script.ALRT_TXT, show_alert=True)
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏꜰ ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ, ꜰɪʀꜱᴛ ᴊᴏɪɴ", show_alert=True)

    elif query.data.startswith("reject"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            types.InlineKeyboardButton("✗ ʀᴇᴊᴇᴄᴛ ✗", callback_data=f"rj_alert#{user_id}")
        ]]
        btn = [[
            types.InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(types.InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>sᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ʀᴇᴊᴇᴄᴛᴇᴅ 😶</b>", reply_markup=types.InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nsᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ʀᴇᴊᴇᴄᴛᴇᴅ 😶</b>", reply_markup=types.InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("accept"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            types.InlineKeyboardButton("😊 ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ 😊", callback_data=f"already_available#{user_id}#{msg_id}")
        ],[
            types.InlineKeyboardButton("‼️ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ‼️", callback_data=f"not_available#{user_id}#{msg_id}")
        ],[
            types.InlineKeyboardButton("🥵 ᴛᴇʟʟ ᴍᴇ ʏᴇᴀʀ 🥵", callback_data=f"year#{user_id}#{msg_id}")
        ],[
            types.InlineKeyboardButton("🙃 ᴜᴘʟᴏᴀᴅᴇᴅ ɪɴ 1 ʜᴏᴜʀ 🙃", callback_data=f"upload_in#{user_id}#{msg_id}")
        ],[
            types.InlineKeyboardButton("☇ ᴜᴘʟᴏᴀᴅᴇᴅ ☇", callback_data=f"uploaded#{user_id}#{msg_id}")
        ]]
        try:
            st = await client.get_chat_member(chnl_id, userid)
            if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
                await query.message.edit_reply_markup(types.InlineKeyboardMarkup(buttons))
            elif st.status == enums.ChatMemberStatus.MEMBER:
                await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏꜰ ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ, ꜰɪʀꜱᴛ ᴊᴏɪɴ", show_alert=True)

    elif query.data.startswith("not_available"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            InlineKeyboardButton("🚫 ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🚫", callback_data=f"na_alert#{user_id}")
        ]]
        btn = [[
            InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>sᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 😢</b>", reply_markup=InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nsᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 😢</b>", reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            InlineKeyboardButton("🙂 ᴜᴘʟᴏᴀᴅᴇᴅ 🙂", callback_data=f"ul_alert#{user_id}")
        ]]
        btn = [[
            InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴜᴘʟᴏᴀᴅᴇᴅ ☺️</b>", reply_markup=InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴜᴘʟᴏᴀᴅᴇᴅ ☺️</b>", reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("already_available"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            InlineKeyboardButton("🫤 ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ 🫤", callback_data=f"aa_alert#{user_id}")
        ]]
        btn = [[
            InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ 😋</b>", reply_markup=InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ 😋</b>", reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("upload_in"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            InlineKeyboardButton("😌 ᴜᴘʟᴏᴀᴅ ɪɴ 1 ʜᴏᴜʀꜱ 😌", callback_data=f"upload_alert#{user_id}")
        ]]
        btn = [[
            InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴜᴘʟᴏᴀᴅᴇᴅ ᴡɪᴛʜɪɴ 1 ʜᴏᴜʀ 😁</b>", reply_markup=InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴜᴘʟᴏᴀᴅᴇᴅ ᴡɪᴛʜɪɴ 1 ʜᴏᴜʀ 😁</b>", reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("year"):
        ident, user_id, msg_id = query.data.split("#")
        chnl_id = query.message.chat.id
        userid = query.from_user.id
        buttons = [[
            InlineKeyboardButton("⚠️ ᴛᴇʟʟ ᴍᴇ ʏᴇᴀʀꜱ ⚠️", callback_data=f"yrs_alert#{user_id}")
        ]]
        btn = [[
            InlineKeyboardButton("♻️ ᴠɪᴇᴡ sᴛᴀᴛᴜs ♻️", url=f"{query.message.link}")
        ]]
        st = await client.get_chat_member(chnl_id, userid)
        if (st.status == enums.ChatMemberStatus.ADMINISTRATOR) or (st.status == enums.ChatMemberStatus.OWNER):
            user = await client.get_users(user_id)
            request = query.message.text
            await query.answer("Message sent to requester")
            await query.message.edit_text(f"<s>{request}</s>")
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            try:
                await client.send_message(chat_id=user_id, text="<b>ʙʀᴏ ᴘʟᴇᴀꜱᴇ ᴛᴇʟʟ ᴍᴇ ʏᴇᴀʀꜱ, ᴛʜᴇɴ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ 😬</b>", reply_markup=InlineKeyboardMarkup(btn))
            except UserIsBlocked:
                await client.send_message(Config.REQUEST_CHANNEL, text=f"<b>💥 ʜᴇʟʟᴏ {user.mention},\n\nʙʀᴏ ᴘʟᴇᴀꜱᴇ ᴛᴇʟʟ ᴍᴇ ʏᴇᴀʀꜱ , ᴛʜᴇɴ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ 😬</b>", reply_markup=InlineKeyboardMarkup(btn), reply_to_message_id=int(msg_id))
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("rj_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("sᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ʀᴇᴊᴇᴄᴛ", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("na_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("sᴏʀʀʏ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("ul_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴜᴘʟᴏᴀᴅᴇᴅ", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("aa_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("upload_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴜᴘʟᴏᴀᴅᴇᴅ ᴡɪᴛʜɪɴ 1 ʜᴏᴜʀ 😁", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)

    elif query.data.startswith("yrs_alert"):
        ident, user_id = query.data.split("#")
        userid = query.from_user.id
        if str(userid) in user_id:
            await query.answer("ʙʀᴏ ᴘʟᴇᴀꜱᴇ ᴛᴇʟʟ ᴍᴇ ʏᴇᴀʀꜱ, ᴛʜᴇɴ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅ 😬", show_alert=True)
        else:
            await query.answer(script.ALRT_TXT, show_alert=True)



    elif query.data.startswith("batchfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        try:
            await query.answer(url=f"https://telegram.me/{Cache.U_NAME}?start=all_{key}")
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{Cache.U_NAME}?start=all_{key}")

    
    elif query.data == "translatemm":
        btn = [        
            [InlineKeyboardButton("Translate English", callback_data="translateen")],    
            [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(Config.PAYMENT_QR)
        )
        await query.message.edit_text(
            text=Config.PAYMENT_TEXTMM,
            reply_markup=reply_markup
        )

    elif query.data == "translateen":
        btn = [        
            [InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],    
            [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(Config.PAYMENT_QR)
        )
        await query.message.edit_text(
            text=Config.PAYMENT_TEXT,
            reply_markup=reply_markup
        )

    elif query.data.startswith("delfile"):
        ident, file_id = query.data.split("#")
        await query.answer(url=f"https://telegram.me/{Cache.U_NAME}?start=files_{file_id}")
