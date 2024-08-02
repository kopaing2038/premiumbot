
import logging, asyncio, time, pytz, re, os, math, json, random, base64
from pyrogram import errors, filters, types, Client, enums
from TechKP.config.Script import script
from ..config import Config
from ..database import a_filter, b_filter, db1, db2, usersDB
from ..utils.botTools import (
    check_fsub,
    format_buttons,
    get_size,
    unpack_new_file_id,
    FORCE_TEXT,
    check_verification,
    get_status,
    handle_next_back,
    get_time
)
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster
from ..utils.logger import LOGGER
from ..utils.decorators import is_banned
from datetime import datetime, timedelta, date
from pyrogram.file_id import FileId
from TechKP.database.db import db
from TechKP.database.join_reqs import JoinReqs
from shortzy import Shortzy
from psutil import virtual_memory, disk_usage, cpu_percent, boot_time


log = LOGGER(__name__)
join_db = JoinReqs


START_TEXT = """Hey {mention} 👋
Iam An Advanced AutoFilter Bot

**@Movie_Zone_KP**
"""

HELP_TEXT = START_TEXT




@Client.on_message(filters.command("start") & filters.incoming)  # type: ignore
@is_banned
async def start_handler(bot: Client, msg: types.Message):
    curr_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    if len(msg.command) > 1:
        _, cmd = msg.command
        if cmd.startswith("filter"):
            #if not await check_fsub(bot, msg, cmd):
               # return
            key = cmd.replace("filter", "").strip()
            keyword = Cache.BUTTONS.get(key)
            filter_data = Cache.SEARCH_DATA.get(key)
            if not (keyword and filter_data):
                return await msg.reply("Search Expired\nPlease send movie name again.")
            files, offset, total_results, imdb, g_settings = filter_data

            settings = g_settings

            if settings["PM_IMDB"] and not g_settings["IMDB"]:
                imdb = await get_poster(keyword, file=(files[0])["file_name"])

            sts = await msg.reply("Please Wait...", quote=True)

            batch_link = f"batchfiles#{msg.chat.id}#{msg.id}#{msg.from_user.id}"

            if settings["IS_BUTTON"]:
                btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
            else:
                btn = []


            if offset != "":
                req = msg.from_user.id if msg.from_user else 0
                btn.append(
                    [
                        types.InlineKeyboardButton(
                            text=f"🗓 1/{math.ceil(int(total_results) / 10)}",
                            callback_data="pages",
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
                    [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
                )
            btn.insert(0, 
                [
                    types.InlineKeyboardButton("Pᴏᴘᴜʟᴀʀ Mᴏᴠɪᴇs", callback_data=f"popmovie#{key}")              
               ]
            )  
            cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())

            if imdb:
                cap = Config.TEMPLATE.format(  # type: ignore
                    request=keyword,
                    mention=msg.from_user.mention,
                    remaining=remaining_seconds,
                    **imdb,
                    **locals(),
                )
                Cache.IMDB_CAP[msg.from_user.id] = cap
                if not settings["IS_BUTTON"]:
                    cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                    for file in files:
                        cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""

            
            else:
                if settings["IS_BUTTON"]:
                    cap = f"○ **Query**:{keyword}\n○ **Total Results**: {total_results}\n○ **Request By**: {msg.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
                else:
                    cap = f"○ **Query**:{keyword}\n○ **Total Results**: {total_results}\n○ **Request By**: {msg.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
                    cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                    for file in files:
                        cap += f"""<b>\n○ <a href="https://telegram.me/{bot.me.username}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""


            if imdb and imdb.get("poster") and settings["PM_IMDB_POSTER"]:
                try:
                    k = await msg.reply_photo(
                        photo=imdb.get("poster"),  # type: ignore
                        caption=cap,
                        reply_markup=types.InlineKeyboardMarkup(btn),
                        quote=True,
                    )
                    if settings["AUTO_DELETE"]:
                        await asyncio.sleep(Config.DELETE_TIME)
                        await k.delete()
                        try:
                            await msg.delete()
                        except:
                            pass

                except (
                    errors.MediaEmpty,
                    errors.PhotoInvalidDimensions,
                    errors.WebpageMediaEmpty,
                ):
                    pic = imdb.get("poster")
                    poster = pic.replace(".jpg", "._V1_UX360.jpg")
                    k = await msg.reply_photo(
                        photo=poster,
                        caption=cap,
                        reply_markup=types.InlineKeyboardMarkup(btn),
                        quote=True,
                    )
                    if settings["AUTO_DELETE"]:
                        await asyncio.sleep(Config.DELETE_TIME)
                        await k.delete()
                        try:
                            await msg.delete()
                        except:
                            pass

                except Exception as e:
                    log.exception(e)
                    k = await msg.reply_text(
                        cap, reply_markup=types.InlineKeyboardMarkup(btn), quote=True
                    )
                    if settings["AUTO_DELETE"]:
                        await asyncio.sleep(Config.DELETE_TIME)
                        await k.delete()
                        try:
                            await msg.delete()
                        except:
                            pass

            else:
                k = await msg.reply_text(
                    cap,
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                    disable_web_page_preview=True,
                )
                if settings["AUTO_DELETE"]:
                    await asyncio.sleep(Config.DELETE_TIME)
                    await k.delete()
                    try:
                        await msg.delete()
                    except:
                        pass
            await sts.delete()
            return
    if len(msg.command) == 2 and msg.command[1] == 'premium':
        if not await db.has_premium_access(msg.from_user.id):
            btn = [       
                [types.InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],        
                [types.InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
                [types.InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
            ]
            reply_markup = types.InlineKeyboardMarkup(btn)
            await msg.reply_photo(
                photo=Config.PAYMENT_QR,
                caption=Config.PAYMENT_TEXT,
                reply_markup=reply_markup
            )
            return
    if len(msg.command) != 2:
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
            types.InlineKeyboardButton('⌬  Sᴛᴀᴛs  ⌬', callback_data='stats'),
            types.InlineKeyboardButton('🤞🏻  Dᴇᴠᴇʟᴏᴘᴇʀs  🤡', callback_data='admin')
        ]]
        reply_markup = types.InlineKeyboardMarkup(buttons)
        await msg.reply_photo(
            photo=random.choice(Config.START_IMG), 
            caption=script.START_TXT.format(msg.from_user.mention, get_status(), msg.from_user.id),
            reply_markup=reply_markup,
        )
        return
    data = msg.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    if data.startswith("all"):
        files = Cache.GETALL.get(file_id)
        if not files:

            return await msg.reply('<b><i>No such file exist.</b></i>')
        filesarr = []
        if not await db.has_premium_access(msg.from_user.id):
            btn = [       
                [types.InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],        
                [types.InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
                [types.InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
            ]
            reply_markup = types.InlineKeyboardMarkup(btn)
            await msg.reply_photo(
                photo=Config.PAYMENT_QR,
                caption=Config.PAYMENT_TEXT,
                reply_markup=reply_markup
            )
            return

        for file in files:
            file_id = file['_id']
            files_ = await a_filter.get_file_details(file_id)
            if not files_:
                files_ = await b_filter.get_file_details(file_id)

            files1 = files_
            
            user_link = msg.from_user.mention if msg.from_user else "Unknown User" 
            caption = Config.CUSTOM_FILE_CAPTION.format(
                file_name='@MKSVIPLINK1  ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{files1['file_name']}</b></a>",
                file_size=get_size(files1['file_size']),
                caption='@MKSCHANNEL1 ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{files1['caption']}</b></a>",
                user_link=user_link
            )
            button = [[
                types.InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=Config.GROUPS_LINK),
                types.InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=Config.CHANNEL_LINK)
            ],[
                types.InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url="t.me/KOPAINGLAY15")
            ]]
            msgs = await bot.send_cached_media(
                chat_id=msg.from_user.id,
                file_id=files1['file_id'],
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(button)
            )
            filesarr.append(msgs)
        k = await msg.reply(Config.DELETE_TEXT, quote=True)
        await asyncio.sleep(300)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return   

    user = msg.from_user.id
    files_ = await a_filter.get_file_details(file_id) 
    if not files_:
        files_ = await b_filter.get_file_details(file_id) 
        if not files_:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:
                if not await db.has_premium_access(msg.from_user.id):
                    btn = [       
                        [types.InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],        
                        [types.InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/{OWNER_USERNAME}")],
                        [types.InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
                    ]
                    reply_markup = types.InlineKeyboardMarkup(btn)
                    await msg.reply_photo(
                        photo=Config.PAYMENT_QR,
                        caption=Config.PAYMENT_TEXT,
                        reply_markup=reply_markup
                    )
                    return

                files = files_[0]


                button = [[
                   types.InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=Config.GROUPS_LINK),
                   types.InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=Config.CHANNEL_LINK)
                ],[
                    types.InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url="t.me/KOPAINGLAY15")
                ]]
                msgs = await bot.send_cached_media(
                    chat_id=msg.from_user.id,
                    file_id=files['file_id'],
                    reply_markup=types.InlineKeyboardMarkup(button)
                )
                filetype = msgs.media
                file = getattr(msgs, filetype.value)
                user_link = msg.from_user.mention if msg.from_user else "Unknown User" 
                caption = Config.CUSTOM_FILE_CAPTION.format(
                    file_name='@MKSVIPLINK1  ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{file['file_name']}</b></a>",
                    file_size=get_size(file['file_size']),
                    caption='@MKSCHANNEL1 ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{file['caption']}</b></a>",
                    user_link=user_link
                )
                await msgs.edit_caption(
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(button)
                )
                btn = [[
                    types.InlineKeyboardButton("Get File Again", callback_data=f'delfile#{file_id}')
                ]]
                k = await msg.reply(Config.DELETE_TEXT,quote=True)
                await asyncio.sleep(300)
                await msg.delete()
                await k.edit_text("<b>ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကို(မူပိုင်ခွင့်ပြဿနာများကြောင့်) ဖျက်ပြီးပါပြီ!!!</b>\n\n<b>ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကိုပြန်ယူရန် အောက်ပါ ခလုတ်ကို နှိပ်ပါ 👇</b>\n\n<b>Your File/Video is successfully deleted!!!\n\nClick below button to get your deleted file 👇</b>",reply_markup=types.InlineKeyboardMarkup(btn))
                return
            except:
                pass
            return await msg.reply('No such file exist.')

    files = files_
    cur_time = datetime.now(pytz.timezone('Asia/Yangon')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    dc_id=FileId.decode(files['file_id']).dc_id 
    user_link = msg.from_user.mention if msg.from_user else "Unknown User" 
    caption = Config.CUSTOM_FILE_CAPTION.format(
        file_name='@MKSVIPLINK1  ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{files['file_name']}</b></a>",
        file_size=get_size(files['file_size']),
        caption='@MKSCHANNEL1 ' + f"<a href='https://t.me/+z5lhEpxP5Go4MWM1'><b>{files['caption']}</b></a>",
        user_link=user_link
    )
    if not await db.has_premium_access(msg.from_user.id):
        btn = [       
            [types.InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],        
            [types.InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
            [types.InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = types.InlineKeyboardMarkup(btn)
        await msg.reply_photo(
            photo=Config.PAYMENT_QR,
            caption=Config.PAYMENT_TEXT,
            reply_markup=reply_markup
        )
        return

    button = [[
        types.InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=Config.GROUPS_LINK),
        types.InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=Config.CHANNEL_LINK)
    ],[
        types.InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url="https://t.me/KOPAINGLAY15")
    ]]
            
    msgs = await bot.send_cached_media(
        chat_id=msg.from_user.id,
        file_id=files['file_id'],
        caption=caption + f"🔋 Data Center ID : <code>{dc_id}</code>\n🚀 ဇာတ်ကားရှာဖွေမူမြန်နှုန်း {remaining_seconds} seconds</b>\n\n@Movie_Zone_KP",
        reply_markup=types.InlineKeyboardMarkup(button)
    )
    btn = [[
        types.InlineKeyboardButton("Get File Again", callback_data=f'delfile#{file_id}')
    ]]
    k = await msg.reply(Config.DELETE_TEXT, quote=True)
    await asyncio.sleep(300)
    await msgs.delete()
    await k.edit_text("<b>ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကို(မူပိုင်ခွင့်ပြဿနာများကြောင့်) ဖျက်ပြီးပါပြီ!!!</b>\n\n<b>ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကိုပြန်ယူရန် အောက်ပါ ခလုတ်ကို နှိပ်ပါ 👇</b>\n\n<b>Your File/Video is successfully deleted!!!\n\nClick below button to get your deleted file 👇</b>",reply_markup=types.InlineKeyboardMarkup(btn))
    return   



@Client.on_callback_query(filters.regex("helps"))  # type: ignore
async def help_handler_query(bot: Client, query: types.CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        HELP_TEXT,
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("◀️ Back", callback_data="back_home")]]
        ),
    )


@Client.on_callback_query(filters.regex("back"))  # type: ignore
async def home_handler(bot: Client, query: types.CallbackQuery):
    await query.answer()
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
        types.InlineKeyboardButton('🤞🏻 ᴇᴀʀɴ ᴍᴏɴᴇʏ ᴡɪᴛʜ ʙᴏᴛ 🤡', callback_data='earn')
    ]]
    reply_markup = types.InlineKeyboardMarkup(buttons)            
    await query.edit_message_media(
        media=types.InputMediaPhoto(
            media=random.choice(Config.START_IMG),
            caption=script.START_TXT.format(query.from_user.mention, get_status(), query.from_user.id)
        ),
        reply_markup=reply_markup
    )

@Client.on_message(filters.command("help") & filters.incoming)  # type: ignore
async def help_handler(bot: Client, msg: types.Message):
    await msg.reply(HELP_TEXT)


@Client.on_message(filters.command("stats"))  # type: ignore
async def get_stats(_, msg: types.Message):
    msgs = await msg.reply("Fetching MongoDb DataBase")
    
    try:
        totalp = await a_filter.col.count_documents({})
        totalsec = await b_filter.col.count_documents({})
        users = await db.get_uall_user()
        chats = await db.get_all_chats()
        premium_users = await db.get_all_premium()
        
        stats = await db1.command('dbStats')
        used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
        free_dbSize = 512 - used_dbSize
        
        stats2 = await db2.command('dbStats')
        used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
        free_dbSize2 = 512 - used_dbSize2
        
        cpu = cpu_percent()
        bot_uptime = get_time(time.time() - Cache.BOT_START_TIME)
        total_disk = get_size(disk_usage('/').total)
        used_disk = get_size(disk_usage('/').used)
        total_ram = get_size(virtual_memory().total)
        used_ram = get_size(virtual_memory().used)
        os_uptime = get_time(time.time() - boot_time())
        
        formatted_text = script.STATUS_TXT.format(
            (int(totalp) + int(totalsec)), 
            premium_users, 
            users, 
            chats, 
            totalp, 
            round(used_dbSize, 2), 
            round(free_dbSize, 2), 
            totalsec, 
            round(used_dbSize2, 2), 
            round(free_dbSize2, 2), 
            cpu, 
            used_disk, 
            total_disk, 
            used_ram, 
            total_ram, 
            bot_uptime, 
            os_uptime
        )
        
        await msgs.edit_text(text=formatted_text)
    
    except Exception as e:
        await msgs.edit_text(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")


@Client.on_message(filters.command("delete") & filters.user(Config.ADMINS))  # type: ignore
async def handleDelete(bot: Client, msg: types.Message):
    """Delete file from database"""
    reply = msg.reply_to_message
    if reply and reply.media:
        msg = await msg.reply("Processing...⏳", quote=True)
    else:
        await msg.reply(
            "Reply to file with /delete which you want to delete", quote=True
        )
        return

    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit("This is not supported file format")
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await a_filter.col.delete_one(
        {
            "_id": file_id,
        }
    )  # type: ignore
    if file_type == "photo":
        result = await a_filter.col.delete_one(
            {
                "file_ref": media.file_id,
            }
        )  # type: ignore
    if result.deleted_count:
        await msg.edit("File is successfully deleted from database")
    else:
        if file_type != "photo":
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await a_filter.col.delete_many(
                {
                    "file_name": file_name,
                    "file_size": media.file_size,
                    "mime_type": media.mime_type,
                }
            )  # type: ignore
            if result.deleted_count:
                return await msg.edit("File is successfully deleted from database")

        await msg.edit("File not found in database")


@Client.on_message(filters.command("search"))
async def search_files(bot, message):
    if message.from_user.id not in Config.ADMINS:
        await message.reply('Only the bot owner can use this command... 😑')
        return
    try:
        keyword = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>")
    files, total = await a_filter.get_bad_files(keyword)
    file_names = "\n\n".join(f"{index + 1}. {item['file_name']}" for index, item in enumerate(files))
    file_data = f"🚫 Your search - '{keyword}':\n\n{file_names}"    
    with open("file_names.txt", "w" , encoding='utf-8') as file:
        file.write(file_data)
    await message.reply_document(
        document="file_names.txt",
        caption=f"<b>♻️ ʙʏ ʏᴏᴜʀ ꜱᴇᴀʀᴄʜ, ɪ ꜰᴏᴜɴᴅ - <code>{total}</code> ꜰɪʟᴇs</b>",
        parse_mode=enums.ParseMode.HTML
    )
    os.remove("file_names.txt")

    files2, total2 = await b_filter.get_bad_files(keyword)
    if int(total2) == 0:
        await message.reply_text('<i>I could not find any files with this keyword 😐</i>')
        return 
    file_names = "\n\n".join(f"{index + 1}. {item['file_name']}" for index, item in enumerate(files2))
    file_data = f"🚫 Your search - '{keyword}':\n\n{file_names}"    
    with open("file_names.txt", "w" , encoding='utf-8') as file:
        file.write(file_data)
    await message.reply_document(
        document="file_names.txt",
        caption=f"<b>♻️ ʙʏ ʏᴏᴜʀ ꜱᴇᴀʀᴄʜ, ɪ ꜰᴏᴜɴᴅ - <code>{total2}</code> ꜰɪʟᴇs 2</b>",
        parse_mode=enums.ParseMode.HTML
    )
    os.remove("file_names.txt")


@Client.on_message(filters.regex("#request"))
async def send_request(bot, message):
    try:
        request = message.text.split(" ", 1)[1]
    except:
        await message.reply_text("<b>‼️ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪs ɪɴᴄᴏᴍᴘʟᴇᴛᴇ</b>")
        return
    buttons = [[
        types.InlineKeyboardButton('👀 ᴠɪᴇᴡ ʀᴇǫᴜᴇꜱᴛ 👀', url=f"{message.link}")
    ],[
        types.InlineKeyboardButton('⚙ sʜᴏᴡ ᴏᴘᴛɪᴏɴ ⚙', callback_data=f'show_options#{message.from_user.id}#{message.id}')
    ]]
    sent_request = await bot.send_message(Config.REQUEST_CHANNEL, script.REQUEST_TXT.format(message.from_user.mention, message.from_user.id, request), reply_markup=types.InlineKeyboardMarkup(buttons))
    btn = [[
         types.InlineKeyboardButton('✨ ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ✨', url=f"{sent_request.link}")
    ]]
    await message.reply_text("<b>✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ, ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ꜱᴏᴍᴇᴛɪᴍᴇ...</b>", reply_markup=types.InlineKeyboardMarkup(btn))




@Client.on_message(filters.private & filters.command('chats') & filters.user(Config.ADMINS))
async def chat_list_users(client, message):
    chat, offset, total, max_btn = await handle_next_back(await db.get_all_group(), max_results=30)
   
    # Generate pagination buttons
    page_number = math.ceil(offset / max_btn) + 1
    total_pages = math.ceil(total / max_btn)
    btn = []

    if offset != 0:
        btn.append([
            types.InlineKeyboardButton("Back", callback_data=f"chat_next#{offset - max_btn}"),
        ])

    btn.append([
        types.InlineKeyboardButton(f"Page {page_number} / {total_pages}", callback_data='bar'),
    ])

    if offset + max_btn < total:
        btn.append([
            types.InlineKeyboardButton("Next", callback_data=f"chat_next#{offset + max_btn}"),
        ])

    btn_markup = types.InlineKeyboardMarkup(btn)
    
    msg = await message.reply('<b>Searching...</b>')
    chats = await db.get_all_chats()
    out = "Groups saved in the database:\n\n"
    count = 1
    async for chat in chats:
        chat_info = await client.get_chat(chat['id'])
        members_count = chat_info.members_count if chat_info.members_count else "Unknown"
        out += f"<b>{count}. Title - `{chat['title']}`\nID - `{chat['id']}`\nMembers - `{members_count}`</b>"
        out += '\n\n'
        count += 1
    
    if count > 1:
        await msg.edit_text(out, reply_markup=btn_markup)
    else:
        await msg.edit_text("<b>No groups found</b>")

@Client.on_callback_query(filters.regex(r"^chat_next"))
async def chat_next_page(client, query):
    _, offset = query.data.split("#")
    offset = int(offset)
    chat, n_offset, total, max_btn = await handle_next_back(await db.get_all_group(), offset=offset, max_results=30)
    
    page_number = math.ceil(n_offset / max_btn) + 1
    total_pages = math.ceil(total / max_btn)
    btn = []

    if n_offset != 0:
        btn.append([
            types.InlineKeyboardButton("Back", callback_data=f"chat_next#{n_offset - max_btn}"),
        ])

    btn.append([
        types.InlineKeyboardButton(f"Page {page_number} / {total_pages}", callback_data='bar'),
    ])

    if n_offset + max_btn < total:
        btn.append([
            types.InlineKeyboardButton("Next", callback_data=f"chat_next#{n_offset + max_btn}"),
        ])

    btn_markup = types.InlineKeyboardMarkup(btn)
    
    chats = await db.get_all_chats()
    out = "Groups saved in the database:\n\n"
    count = 1
    async for chat in chats:
        chat_info = await client.get_chat(chat['id'])
        members_count = chat_info.members_count if chat_info.members_count else "Unknown"
        out += f"<b>{count}. Title - `{chat['title']}`\nID - `{chat['id']}`\nMembers - `{members_count}`</b>"
        out += '\n\n'
        count += 1
    
    if count > 1:
        await query.message.edit_text(out, reply_markup=btn_markup)
    else:
        await query.message.edit_text("<b>No groups found</b>")

@Client.on_message(filters.command("restart") & filters.user(Config.ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("totalrequests") & filters.private & filters.user(Config.ADMINS))
async def total_requests(client, message):
    if join_db().isActive():
        total = await join_db().get_all_users_count()
        await message.reply_text(
            text=f"Total Requests: {total}",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

@Client.on_message(filters.command("purgerequests") & filters.private & filters.user(Config.ADMINS))
async def purge_requests(client, message):   
    if join_db().isActive():
        await join_db().delete_all_users()
        await message.reply_text(
            text="Purged All Requests.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
