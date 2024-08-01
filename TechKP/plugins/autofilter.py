import math 
import re
import logging, asyncio, time, pytz, re, os
from imdb import Cinemagoer
from pyrogram import Client, enums, errors, filters, types
import traceback
from fuzzywuzzy import process
from ..config import Config
from ..database import a_filter, b_filter
from ..database import configDB as config_db
from ..utils.botTools import check_fsub, format_buttons, get_size, parse_link, get_cap, get_cap2, get_status
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster
from ..utils.logger import LOGGER
from TechKP.config.Script import script
from TechKP.utils.imdbDB import imdb_get_poster
from datetime import datetime, timedelta, date
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from imdb import Cinemagoer 
from pyrogram.types import CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from TechKP.database.db import db

im_db = Cinemagoer() 
log = LOGGER(__name__)


@Client.on_message(filters.group & filters.text & filters.incoming, group=-1)  # type: ignore
async def group_search(client, message):
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")

    if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
        total=await client.get_chat_members_count(message.chat.id)
        group_link = await message.chat.export_invite_link()
        user = message.from_user.mention if message.from_user else "Dear" 
        await client.send_message(Config.LOG_CHANNEL, script.NEW_GROUP_TXT.format(Cache.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user))       
        await db.add_chat(message.chat.id, message.chat.title)
        return 

    if settings["AUTO_FILTER"]:
        if not user_id:
            await message.reply("<b>🚨 ɪ'ᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ғᴏʀ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ!</b>")
            return
        

        if message.text.startswith("/"):
            return
        
        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            await message.delete()
            return await message.reply("<b>sᴇɴᴅɪɴɢ ʟɪɴᴋ ɪsɴ'ᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ ❌🤞🏻</b>")

        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        if message.reply_to_message:
                            try:
                                sent_msg = await message.reply_to_message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.reply_to_message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
                        else:
                            try:
                                sent_msg = await message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
            hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
            await message.reply_text('<code>Report sent</code>' + ''.join(hidden_mentions))
            return               
        else:
            try: 
                await auto_filter(client, message)
            except Exception as e:
                traceback.print_exc()
                print('found err in grp search  :',e)

    else:
        k=await message.reply_text('<b>⚠️ ᴀᴜᴛᴏ ғɪʟᴛᴇʀ ᴍᴏᴅᴇ ɪꜱ ᴏғғ...</b>')
        await asyncio.sleep(5)
        await k.delete()
        try:
            await message.delete()
        except:
            pass



async def auto_filter(bot: Client, msg: types.Message, spoll=False , pm_mode = False):
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()

    if not spoll:
        message = msg
        search = message.text
        chat_id = message.chat.id


        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER']
        )
        if not files:
            if settings["SPELL_CHECK"]:
                ai_sts = await msg.reply_text('<b>Ai is Cheking For Your Spelling. Please Wait.</b>')
                is_misspelled = await ai_spell_check(search)
                if is_misspelled:
                    await ai_sts.edit(f'<b>Ai Suggested <code>{is_misspelled}</code>\nSo Im Searching for <code>{is_misspelled}</code></b>')
                    await asyncio.sleep(2)
                    msg.text = is_misspelled
                    await ai_sts.delete()
                    return await auto_filter(bot, msg)
                await ai_sts.delete()
                return await advantage_spell_chok(msg)
            return

    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")


    key = f"{message.chat.id}-{message.id}"
    Cache.GETALL[key] = files
    Cache.BUTTONS[key] = search
    
    if settings["IMDB"]:  # type: ignore
        imdb = await get_poster(search, file=(files[0])["file_name"])
    else:
        imdb = {}
    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings

    batch_link = f"batchfiles#{key}"

    if not settings.get("DOWNLOAD_BUTTON"):  # type: ignore
        if settings["IS_BUTTON"]:
            btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
        else:
            btn = []
        if offset != "":
            req = message.from_user.id if message.from_user else 0
            btn.append(
                [
                    types.InlineKeyboardButton(
                        text=f"🗓 1/{math.ceil(int(total_results) / 10)}",
                        callback_data="pages",
                    ),
                    types.InlineKeyboardButton(
                        text=f"Total {total_results}", callback_data="pages",
                    ),
                    types.InlineKeyboardButton(
                        text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
                    ),
                ]
            )
            btn_1 = []
            if settings.get('IS_QUALITIES'):
                btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"qualities#{key}#{0}#{req}"))
   
            if settings.get('IS_EPISODES'):     
                btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"episodes#{req}#{key}#{0}"))

            if settings.get('IS_SEASONS'):     
                btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seasons#{key}#{0}#{req}"))
        
            if btn_1:
                btn.insert(0, btn_1)

            btn_2 = []

            if settings.get('IS_SENDALL'):     
                btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

            if settings.get('IS_YEARS'):     
                btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"years#{key}#{0}#{req}"))

            btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

            if btn_2:
                btn.insert(0, btn_2)


        else:
            btn.append(
                [types.InlineKeyboardButton(text=f"🗓 1/1 || Total: {total_results}", callback_data="pages")]
            )
          
        btn.insert(0, 
            [
                types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
            ]
        )  
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    "Download", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    k = 1
    cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    if imdb:
        cap = Config.TEMPLATE.format(  # type: ignore
            request=search,
            mention=message.from_user.mention,
            remaining=remaining_seconds,
            **imdb,
            **locals(),
        )
        Cache.IMDB_CAP[message.from_user.id] = cap
        if not settings.get("DOWNLOAD_BUTTON"):
            if not settings["IS_BUTTON"]:
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
            
    else:
        if settings["IS_BUTTON"]:
            cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
        else:
            cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
            if not settings.get("DOWNLOAD_BUTTON"):
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""

    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:  # type: ignore
        try:
            k = await message.reply_photo(
                photo=imdb.get("poster"),  # type: ignore
                caption=cap,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True,
            )
            if settings["AUTO_DELETE"]:
                await asyncio.sleep(Config.DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass


        except (
            errors.MediaEmpty,
            errors.PhotoInvalidDimensions,
            errors.WebpageMediaEmpty,
        ):
            pic = imdb.get("poster")
            poster = pic.replace(".jpg", "._V1_UX360.jpg")
            k = await message.reply_photo(
                photo=poster,
                caption=cap,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True,
            )
            if settings["AUTO_DELETE"]:
                await asyncio.sleep(Config.DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except Exception as e:
            log.exception(e)
            await message.reply_text(
                cap, reply_markup=types.InlineKeyboardMarkup(btn), quote=True
            )
            if settings["AUTO_DELETE"]:
                await asyncio.sleep(Config.DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
    else:
        k = await message.reply_text(
            cap,
            reply_markup=types.InlineKeyboardMarkup(btn),
            quote=True,
            disable_web_page_preview=True,
        )
        if settings["AUTO_DELETE"]:
            await asyncio.sleep(Config.DELETE_TIME)
            await k.delete()
            try:
                await message.delete()
            except:
                pass

@Client.on_callback_query(filters.regex(r"^next"))  # type: ignore
async def next_page(bot: Client, query: types.CallbackQuery):
    _, req, key, offset = query.data.split("_")  # type: ignore
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer(
            "You are using one of my old messages, please send the request again.",
            show_alert=True,
        )
        return
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")

    files, n_offset, total = await a_filter.get_search_results(
        search, offset=offset, filter=True, photo=settings['PHOTO_FILTER']
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []
    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                    callback_data="pages",
                ),
            ]
        )
    elif off_set is None:
        btn.append(
            [
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ],
        )
    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"qualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"episodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seasons#{key}#{0}#{req}"))
        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"years#{key}#{0}#{req}"))

    btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)

    btn.insert(0, 
        [
            types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
        ]
    )
    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()




@Client.on_callback_query(filters.regex(r"^qualities#"))
async def quality_cb_handler(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn= []
    for i in range(0, len(Config.QUALITIES)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i].title(),
                callback_data=f"quality_search#{Config.QUALITIES[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i+1].title(),
                callback_data=f"quality_search#{Config.QUALITIES[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i+2].title(),
                callback_data=f"quality_search#{Config.QUALITIES[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ǫᴜᴀʟɪᴛʏ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^quality_search#"))
async def quality_search(client: Client, query: types.CallbackQuery):
    _, qul, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS.get(key)
    IMDB_CAP = Cache.IMDB_CAP.get(query.from_user.id)
    if not search:
        await query.answer(
            "You are using one of my old messages, please send the request again.",
            show_alert=True,
        )
        return
    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await a_filter.get_search_results(
        f"{search} {qul}", offset=offset, filter=True, photo=settings['PHOTO_FILTER']
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(qul, file['file_name'], re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ǫᴜᴀʟɪᴛʏ {qul.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return
    batch_link = f"batchfiles#{key}"
    Cache.GETALL[key] = files
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"quality_search#{qul}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"quality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"quality_search#{qul}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"quality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn_1 = []
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"episodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seasons#{key}#{0}#{req}"))

        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []

    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"years#{key}#{0}#{req}"))

    btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)
    btn.insert(0, 
        [
            types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
        ]
    )
    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{orginal_offset}"),])

    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: types.CallbackQuery):

    ident, req, key, original_offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer("Don't Click Other Results! ⚠️", show_alert=True)

    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer("You clicking my old message, Please request again. 🙂", show_alert=True)
        return
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(Config.EPISODES)-1, 6):
        row = []
        for j in range(6):
            if i+j < len(Config.EPISODES):
                row.append(
                    types.InlineKeyboardButton(
                        text=Config.EPISODES[i+j].title(),
                        callback_data=f"fe#{req}#{key}#{Config.EPISODES[i+j].lower()}#{original_offset}"

                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            types.InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴇᴘɪsᴏᴅᴇ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{original_offset}")])
    await query.edit_message_reply_markup(types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: types.CallbackQuery):
    _, req, key, episode, original_offset = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer("Don't Click Other Results! ⚠️", show_alert=True)
    
    # Convert original_offset to an integer
    original_offset = int(original_offset)
    
    search = Cache.BUTTONS.get(key)
    IMDB_CAP = Cache.IMDB_CAP.get(query.from_user.id)
    
    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)
    
    search = search.replace('_', ' ')
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await a_filter.get_search_results(
        f"{search} {episode}", offset=original_offset, filter=True, photo=settings['PHOTO_FILTER']
    )
    if not files:
        return await query.answer(f"No results found for episode {episode}.", show_alert=True)
    
    batch_link = f"batchfiles#{key}"
    Cache.GETALL[key] = files
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    
    if n_offset == '':
        btn.append([types.InlineKeyboardButton(text="🚸 No More Pages 🚸", callback_data="buttons")])

    elif n_offset == 0:
        btn.append([
            types.InlineKeyboardButton("⪻ Back", callback_data=f"fe#{req}#{key}#{episode}#{original_offset - 8}"),
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
        ])
    elif original_offset == 0:
        btn.append([
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
            types.InlineKeyboardButton("Next ⪼", callback_data=f"fe#{req}#{key}#{episode}#{n_offset}"),
        ])
    else:
        btn.append([
            types.InlineKeyboardButton("⪻ Back", callback_data=f"fe#{req}#{key}#{episode}#{original_offset - 8}"),
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
            types.InlineKeyboardButton("Next ⪼", callback_data=f"fe#{req}#{key}#{episode}#{n_offset}"),
        ])
    
    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"qualities#{key}#{0}#{req}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seasons#{key}#{0}#{req}"))
   
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []

    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"years#{key}#{0}#{req}"))

    btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)
    btn.insert(0, 
        [
            types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
        ]
    )
    btn.append([types.InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{0}")])
    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True) 
    btn= []
    for i in range(0, len(Config.SEASONS)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.SEASONS[i].title(),
                callback_data=f"season_search#{Config.SEASONS[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.SEASONS[i+1].title(),
                callback_data=f"season_search#{Config.SEASONS[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.SEASONS[i+2].title(),
                callback_data=f"season_search#{Config.SEASONS[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])

    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ sᴇᴀsᴏɴ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^season_search#"))
async def season_search(client: Client, query: types.CallbackQuery):
    _, season, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    seas = int(season.split(' ' , 1)[1])
    if seas < 10:
        seas = f'S0{seas}'
    else:
        seas = f'S 0{seas}'

    seass = int(season.split(' ' , 1)[1])
    if seass < 10:
        seass = f'Season0{seas}'
    else:
        seass = f'Season 0{seas}'



    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)
    search = Cache.BUTTONS.get(key)
    IMDB_CAP = Cache.IMDB_CAP.get(query.from_user.id)
    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)

    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await a_filter.get_search_results(f"{search} {seas}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    files2, n_offset2, total2 = await a_filter.get_search_results(f"{search} {season}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    files3, n_offset3, total3 = await a_filter.get_search_results(f"{search} {seass}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    total += total2
    total += total3
    try:
        n_offset = int(n_offset)
    except:
        try: 
            n_offset = int(n_offset2)
        except : 
            n_offset = 0
    files = [file for file in files if re.search(seas, file['file_name'], re.IGNORECASE)]
    
    if not files:
        files = [file for file in files2 if re.search(season, file['file_name'], re.IGNORECASE)]
        if not files:
            files = [file for file in files3 if re.search(season, file['file_name'], re.IGNORECASE)]
            if not files:
                await query.answer(f"sᴏʀʀʏ {season.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
                return
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []
    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"
    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"qualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"episodes#{req}#{key}#{0}"))

        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"years#{key}#{0}#{req}"))

    btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)

    btn.insert(0, 
        [
            types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
        ]
    )
    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"season_search#{season}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"season_search#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"season_search#{season}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"season_search#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"),])


    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn  = []
    for i in range(0, len(Config.YEARS)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.YEARS[i].title(),
                callback_data=f"years_search#{Config.YEARS[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.YEARS[i+1].title(),
                callback_data=f"years_search#{Config.YEARS[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.YEARS[i+2].title(),
                callback_data=f"years_search#{Config.YEARS[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])
    
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ʏᴇᴀʀ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^years_search#"))
async def year_search(client: Client, query: types.CallbackQuery):
    _, year, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)

    search = Cache.BUTTONS.get(key)
    IMDB_CAP = Cache.IMDB_CAP.get(query.from_user.id)

    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)

    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await a_filter.get_search_results(f"{search} {year}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(year, file['file_name'], re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ʏᴇᴀʀ {year.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return

    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"
    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"years_search#{year}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"years_search#{year}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"years_search#{year}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"years_search#{year}#{key}#{n_offset}#{orginal_offset}#{req}"),])


    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"qualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"episodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seasons#{key}#{0}#{req}"))
        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    btn_2.append(types.InlineKeyboardButton("⚜️ sᴇʀɪᴇs ᴏɴʟʏ", callback_data=f"series#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)

    btn.insert(0, 
        [
            types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
        ]
    )
    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"),])

    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()

#-------------------------------------------------------

@Client.on_callback_query(filters.regex(r"^series#"))
async def series_cb_handler(bot: Client, query: types.CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key, offset, req = query.data.split("#")
    search = Cache.BUTTONS.get(key)

    original_offset = 0
    series_results = im_db.search_movie(search)
    series_list = []
    for result in series_results:
        if result['kind'] == 'tv series':
            series_list.append(result['title'])
    original_offset = 0
    if series_list:
        cap = f"Found 10 series:\n"
        btn = []
        for series in series_list:                                    
            btn.append([types.InlineKeyboardButton(series, callback_data=f"seri#{series[:10]}#{key}#{0}#{offset}#{req}")])
        await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
    else:
        await query.message.edit_text("No series found.")

@Client.on_callback_query(filters.regex(r"^seri#"))
async def request_series_cb_handler(bot: Client, query: types.CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    
    _, search, key, offset, original_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    try:
        offset = int(offset)
    except:
        offset = 0
    
    search = search.replace('_', ' ')
    Cache.BUTTONS2[key] = search
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(f"{search}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    
    files = [file for file in files if re.search(search, file['file_name'], re.IGNORECASE)]
    
    if not files:
        return await query.answer(f"No results found for {search}.", show_alert=True)
    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"
    
    imdb = await get_poster(search, file=(files[0])["file_name"]) if settings.get("IMDB") else {}
    btn= []
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    btn_2 = []

    if n_offset== '':

        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    else:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"sernext#{key}#{n_offset}#{original_offset}#{req}"),])

        btn_1 = []
        if settings.get('IS_QUALITIES'):
            btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"seriesqualities#{key}#{0}#{req}"))
   
        if settings.get('IS_EPISODES'):     
            btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"seriesepisodes#{req}#{key}#{0}"))

        if settings.get('IS_SEASONS'):     
            btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seriesseasons#{key}#{0}#{req}"))
        
        if btn_1:
            btn.insert(0, btn_1)
    


        if settings.get('IS_YEARS'):
            btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"seriesyears#{key}#{0}#{req}"))


    if settings.get('IS_SENDALL'):
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if btn_2:
        btn.insert(0, btn_2)
    
    cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())

    if imdb:
        cap = Config.TEMPLATE.format(  # type: ignore
            request=search,
            mention=query.from_user.mention,
            remaining=remaining_seconds,
            **imdb,
            **locals(),
        )
        Cache.IMDB_CAP2[query.from_user.id] = cap
        if not settings.get("DOWNLOAD_BUTTON"):
            if not settings["IS_BUTTON"]:
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
            
    else:
        if settings["IS_BUTTON"]:
            cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {query.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
        else:
            cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {query.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
            if not settings.get("DOWNLOAD_BUTTON"):
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])

    try:
        if not settings["IS_BUTTON"]:
            await bot.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                types.InputMediaPhoto(imdb.get("poster"))
            )
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        else:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
    except MessageNotModified:
        pass
    
    await query.answer()


@Client.on_callback_query(filters.regex(r"^sernext#"))
async def sernext_search(client: Client, query: types.CallbackQuery):
    _, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)

    search = Cache.BUTTONS2.get(key)

    IMDB_CAP = Cache.IMDB_CAP2.get(query.from_user.id)
    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)

    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(f"{search}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(search, file['file_name'], re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return

    Cache.GETALL[key] = files
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []


    batch_link = f"batchfiles#{key}"
    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"sernext#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"sernext#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"sernext#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"sernext#{key}#{n_offset}#{orginal_offset}#{req}"),])


    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"seriesqualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"seriesepisodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seriesseasons#{key}#{0}#{req}"))
        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"seriesyears#{key}#{0}#{req}"))

    if btn_2:
        btn.insert(0, btn_2)


    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])

    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap2(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^seriesqualities#"))
async def seriesquality_cb_handler(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn= []
    search = Cache.BUTTONS2.get(key)
    for i in range(0, len(Config.QUALITIES)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i].title(),
                callback_data=f"seriesquality_search#{Config.QUALITIES[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i+1].title(),
                callback_data=f"seriesquality_search#{Config.QUALITIES[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.QUALITIES[i+2].title(),
                callback_data=f"seriesquality_search#{Config.QUALITIES[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ǫᴜᴀʟɪᴛʏ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^seriesquality_search#"))
async def seriesquality_search(client: Client, query: types.CallbackQuery):
    _, qul, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS2.get(key)
    IMDB_CAP = Cache.IMDB_CAP2.get(query.from_user.id)
    if not search:
        await query.answer(
            "You are using one of my old messages, please send the request again.",
            show_alert=True,
        )
        return
    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(
        f"{search} {qul}", offset=offset, filter=True, photo=settings['PHOTO_FILTER']
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(qul, file['file_name'], re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ǫᴜᴀʟɪᴛʏ {qul.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return
    batch_link = f"batchfiles#{key}"
    Cache.GETALL[key] = files
    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriesquality_search#{qul}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriesquality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriesquality_search#{qul}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriesquality_search#{qul}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn_1 = []
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"seriesepisodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seriesseasons#{key}#{0}#{req}"))

        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []

    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"seriesyears#{key}#{0}#{req}"))


    if btn_2:
        btn.insert(0, btn_2)

    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{orginal_offset}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])

    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap2(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^seriesepisodes#"))
async def seriesepisodes_cb_handler(client: Client, query: types.CallbackQuery):

    ident, req, key, original_offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer("Don't Click Other Results! ⚠️", show_alert=True)

    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer("You clicking my old message, Please request again. 🙂", show_alert=True)
        return
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(Config.EPISODES)-1, 6):
        row = []
        for j in range(6):
            if i+j < len(Config.EPISODES):
                row.append(
                    types.InlineKeyboardButton(
                        text=Config.EPISODES[i+j].title(),
                        callback_data=f"seriesfe#{req}#{key}#{Config.EPISODES[i+j].lower()}#{original_offset}"

                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            types.InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴇᴘɪsᴏᴅᴇ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{original_offset}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])
    await query.edit_message_reply_markup(types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^seriesfe#"))
async def seriesfilter_episodes_cb_handler(client: Client, query: types.CallbackQuery):
    _, req, key, episode, original_offset = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer("Don't Click Other Results! ⚠️", show_alert=True)
    
    # Convert original_offset to an integer
    original_offset = int(original_offset)
    
    search = Cache.BUTTONS2.get(key)
    IMDB_CAP = Cache.IMDB_CAP2.get(query.from_user.id)
    
    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)
    
    search = search.replace('_', ' ')
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(
        f"{search} {episode}", offset=original_offset, filter=True, photo=settings['PHOTO_FILTER']
    )
    if not files:
        return await query.answer(f"No results found for episode {episode}.", show_alert=True)
    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"

    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []

    
    if n_offset == '':
        btn.append([types.InlineKeyboardButton(text="🚸 No More Pages 🚸", callback_data="buttons")])

    elif n_offset == 0:
        btn.append([
            types.InlineKeyboardButton("⪻ Back", callback_data=f"seriesfe#{req}#{key}#{episode}#{original_offset - 8}"),
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
        ])
    elif original_offset == 0:
        btn.append([
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
            types.InlineKeyboardButton("Next ⪼", callback_data=f"seriesfe#{req}#{key}#{episode}#{n_offset}"),
        ])
    else:
        btn.append([
            types.InlineKeyboardButton("⪻ Back", callback_data=f"fe#{req}#{key}#{episode}#{original_offset - 8}"),
            types.InlineKeyboardButton(f"{math.ceil(int(original_offset) / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages"),
            types.InlineKeyboardButton("Next ⪼", callback_data=f"seriesfe#{req}#{key}#{episode}#{n_offset}"),
        ])
    
    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"seriesqualities#{key}#{0}#{req}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seriesseasons#{key}#{0}#{req}"))
   
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []

    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"seriesyears#{key}#{0}#{req}"))


    if btn_2:
        btn.insert(0, btn_2)

    btn.append([types.InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])
    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap2(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^seriesseasons#"))
async def series_seasonsb_handler_c(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer("You are not authorized to perform this action.", show_alert=True) 
    

    search = Cache.BUTTONS2.get(key)
    seasons = Config.SEASONS

    btn= []
    for i in range(0, len(Config.SEASONS)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.SEASONS[i].title(),
                callback_data=f"seriessearch#{Config.SEASONS[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.SEASONS[i+1].title(),
                callback_data=f"seriessearch#{Config.SEASONS[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.SEASONS[i+2].title(),
                callback_data=f"seriessearch#{Config.SEASONS[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])

    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ sᴇᴀsᴏɴ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^seriessearch#"))
async def seriesse_ason_search(client: Client, query: types.CallbackQuery):
    _, season, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    seas = int(season.split(' ' , 1)[1])
    if seas < 10:
        seas = f'S0{seas}'
    else:
        seas = f'S 0{seas}'

    seass = int(season.split(' ' , 1)[1])
    if seass < 10:
        seass = f'Season0{seas}'
    else:
        seass = f'Season 0{seas}'



    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)
    search = Cache.BUTTONS2.get(key)
    IMDB_CAP = Cache.IMDB_CAP2.get(query.from_user.id)
    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)

    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(f"{search} {seas}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    files2, n_offset2, total2 = await b_filter.get_search_results(f"{search} {season}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    files3, n_offset3, total3 = await b_filter.get_search_results(f"{search} {seass}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    total += total2
    total += total3
    try:
        n_offset = int(n_offset)
    except:
        try: 
            n_offset = int(n_offset2)
        except : 
            n_offset = 0
    files = [file for file in files if re.search(seas, file['file_name'], re.IGNORECASE)]
    
    if not files:
        files = [file for file in files2 if re.search(season, file['file_name'], re.IGNORECASE)]
        if not files:
            files = [file for file in files3 if re.search(season, file['file_name'], re.IGNORECASE)]
            if not files:
                await query.answer(f"sᴏʀʀʏ {season.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
                return

    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []
    Cache.GETALL[key] = files
    batch_link = f"batchfiles#{key}"
    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"seriesqualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"seriesepisodes#{req}#{key}#{0}"))

        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))

    if settings.get('IS_YEARS'):     
        btn_2.append(types.InlineKeyboardButton("🚩 ʏᴇᴀʀ ⌛", callback_data=f"seriesyears#{key}#{0}#{req}"))



    if btn_2:
        btn.insert(0, btn_2)


    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriessearch#{season}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriessearch#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriessearch#{season}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriessearch#{season}#{key}#{n_offset}#{orginal_offset}#{req}"),])

    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{search}{key}#{0}#{0}#{req}")])


    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap2(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^seriesyears#"))
async def seriesyears_cb_handler(client: Client, query: types.CallbackQuery):
    _, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)
    btn  = []
    search = Cache.BUTTONS2.get(key)
    for i in range(0, len(Config.YEARS)-1, 3):
        btn.append([
            types.InlineKeyboardButton(
                text=Config.YEARS[i].title(),
                callback_data=f"seriesyears_search#{Config.YEARS[i].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.YEARS[i+1].title(),
                callback_data=f"seriesyears_search#{Config.YEARS[i+1].lower()}#{key}#0#{offset}#{req}"
            ),
            types.InlineKeyboardButton(
                text=Config.YEARS[i+2].title(),
                callback_data=f"seriesyears_search#{Config.YEARS[i+2].lower()}#{key}#0#{offset}#{req}"
            ),
        ])
    
    btn.append([types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ʏᴇᴀʀ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ ʜᴇʀᴇ ↓↓</b>", reply_markup=types.InlineKeyboardMarkup(btn))
    return

@Client.on_callback_query(filters.regex(r"^seriesyears_search#"))
async def seriesyear_search(client: Client, query: types.CallbackQuery):
    _, year, key, offset, orginal_offset, req = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if int(req) != query.from_user.id:
        return await query.answer(script.ALRT_TXT, show_alert=True)	
    offset = int(offset)

    search = Cache.BUTTONS2.get(key)
    IMDB_CAP = Cache.IMDB_CAP2.get(query.from_user.id)

    if not search:
        return await query.answer("Old request. Please try again.", show_alert=True)

    search = search.replace("_", " ")
   
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
    files, n_offset, total = await b_filter.get_search_results(f"{search} {year}", offset=offset, filter=True, photo=settings['PHOTO_FILTER'])
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files = [file for file in files if re.search(year, file['file_name'], re.IGNORECASE)]
    if not files:
        await query.answer(f"sᴏʀʀʏ ʏᴇᴀʀ {year.title()} ɴᴏᴛ ғᴏᴜɴᴅ ғᴏʀ {search}", show_alert=1)
        return
    Cache.GETALL[key] = files

    if settings["IS_BUTTON"]:
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
    else:
        btn = []


    batch_link = f"batchfiles#{key}"
    if n_offset== '':
        btn.append(
            [types.InlineKeyboardButton(text="🚸 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs 🚸", callback_data="buttons")]
        )
    elif n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriesyears_search#{year}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
            ])
    elif offset==0:
        btn.append(
            [types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}",callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriesyears_search#{year}#{key}#{n_offset}#{orginal_offset}#{req}"),])
    else:
        btn.append(
            [types.InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data=f"seriesyears_search#{year}#{key}#{offset- 8}#{orginal_offset}#{req}"),
             types.InlineKeyboardButton(f"{math.ceil(offset / 8) + 1}/{math.ceil(total / 8)}", callback_data="pages",),
             types.InlineKeyboardButton("ɴᴇxᴛ ⪼", callback_data=f"seriesyears_search#{year}#{key}#{n_offset}#{orginal_offset}#{req}"),])


    btn_1 = []
    if settings.get('IS_QUALITIES'):
        btn_1.append(types.InlineKeyboardButton("✨ ǫᴜᴀʟɪᴛʏ 🤡", callback_data=f"seriesqualities#{key}#{0}#{req}"))
   
    if settings.get('IS_EPISODES'):     
        btn_1.append(types.InlineKeyboardButton("👀 ᴇᴘɪsᴏᴅᴇs ⚜️", callback_data=f"seriesepisodes#{req}#{key}#{0}"))

    if settings.get('IS_SEASONS'):     
        btn_1.append(types.InlineKeyboardButton("✨ Season 🍿", callback_data=f"seriesseasons#{key}#{0}#{req}"))
        
    if btn_1:
        btn.insert(0, btn_1)

    btn_2 = []
    if settings.get('IS_SENDALL'):     
        btn_2.append(types.InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=batch_link))


    if btn_2:
        btn.insert(0, btn_2)


    btn.append([
        types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}"), types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ sᴇʀɪᴇs ᴘᴀɢᴇ", callback_data=f"sernext#{key}#{0}#{0}#{req}")])

    if not settings["IS_BUTTON"]:
        cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap2(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=types.InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=types.InlineKeyboardMarkup(btn)
            )
        except errors.MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^popmovie#"))
async def popmovie_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) != query.message.reply_to_message.from_user.id:
            return await query.answer(
                text=f"⚠️ Hello {query.from_user.first_name},\nThis is not your movie request, request yours...",
                show_alert=True,
            )
    except Exception as e:
        print(f"Error checking user ID: {e}")
    
    _, key = query.data.split("#")
    
    # Assuming 'ia' is your IMDb data retrieval object or function
    popular_movies = im_db.get_popular100_movies()[:25]
    req = query.from_user.id
    response_text = "<b>Top 25 Popular Movies:</b>\n\n"
    for idx, movie in enumerate(popular_movies, start=1):
        title = movie.get('title', 'Unknown Title')
        response_text += f"{idx}. <code>{title}</code>\n"
    
    btn = [[types.InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{0}")]]

    try:
        await query.message.edit_text(
            text=response_text,
            reply_markup=types.InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        print(f"Error editing message: {e}")

@Client.on_callback_query(filters.regex("^file"))  # type: ignore
async def button_file_handle_file(bot: Client, query: types.CallbackQuery):
    if query.data.startswith("file"):
        _, file_unique_id = query.data.split()
        try:
            if int(query.from_user.id) != query.message.reply_to_message.from_user.id:
                return await query.answer(
                    text=f"⚠️ Hello {query.from_user.first_name},\nThis is not your movie request, request yours...",
                    show_alert=True,
                )
        except Exception as e:
            print(f"Error checking user ID: {e}")
        await query.answer(url=f"https://t.me/{bot.me.username}?start=files_{file_unique_id}")



#@Client.on_callback_query(filters.regex("^file"))  # type: ignore
async def handle_file(bot: Client, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info = await a_filter.get_file_details(file_id)  # type: ignore
    if not file_info:
        return await query.answer("FileNotFoundError", True)
    if file_info["file_type"] == "photo":
        file_id = file_info["file_ref"]
    query.message.from_user = query.from_user
    isMsg = query.message.chat.type == enums.ChatType.PRIVATE
    if not await check_fsub(bot, query.message, sendMsg=isMsg):
        if not isMsg:
            return await query.answer(url=f"https://t.me/{bot.me.username}?start=fsub")
        return await query.answer("Please Join My Update Channel and click again")
    try:
        await bot.send_cached_media(
            query.from_user.id,
            file_id,  # type: ignore
            caption=Config.CUSTOM_FILE_CAPTION.format(  # type: ignore
                file_name=file_info["file_name"],
                file_size=get_size(file_info["file_size"]),
                caption=file_info["caption"],
            ),
            reply_to_message_id=query.message.id,
        )
    except errors.PeerIdInvalid:
        return await query.answer(f"https://t.me/{bot.me.username}?start=okok")
    await query.answer(f'Sending : {file_info["file_name"]}')




@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT, show_alert=True)
    movie = await imdb_get_poster(id, id=True)
    search = movie.get('title')
    await query.answer('ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ 🌚')
    files, offset, total_results = await a_filter.get_search_results(search)
    if files:
        k = (search, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        k = await query.message.edit(script.NO_RESULT_TXT)
        await asyncio.sleep(60)
        await k.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

async def ai_spell_check(wrong_name):
    async def search_movie(wrong_name):
        search_results = im_db.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return 
        movie = closest_match[0]
        files, offset, total_results = await a_filter.get_search_results(movie)
        if files:
            return movie
        movie_list.remove(movie)


async def advantage_spell_chok(message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await config_db.get_settings(f"SETTINGS_{chat_id}")
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"
    try:
        movies = await imdb_get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[
            types.InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=types.InlineKeyboardMarkup(button))
        await asyncio.sleep(120)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        types.InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    buttons.append(
        [types.InlineKeyboardButton(text="🚫 ᴄʟᴏsᴇ 🚫", callback_data='close_data')]
    )
    d = await message.reply_text(text=script.CUDNT_FND.format(message.from_user.mention), reply_markup=types.InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await d.delete()
    try:
        await message.delete()
    except:
        pass
