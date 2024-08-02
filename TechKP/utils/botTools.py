import base64, pytz
from struct import pack
from TechKP.config.Script import script
from TechKP.database.db import db
from pyrogram import Client, enums, errors, types
from pyrogram.file_id import FileId
import pytz, re, os 
from shortzy import Shortzy
from datetime import datetime
from ..config import Config
from ..database import configDB as config_db
from .cache import Cache
from .logger import LOGGER
from datetime import datetime, date
from typing import Union
from imdb import Cinemagoer 


log = LOGGER(__name__)
VERIFIED = {}
imdb = Cinemagoer() 

CONFIGURABLE = {
    "AUTO_FILTER": {"help": "Enable / disable AUTO FILTER", "name": "AUTO FILTER"},
    "IMDB": {"help": "Enable or disable IMDB status", "name": "Imdb Info"},
    "CHANNEL": {"help": "Redirect to Channel / Send File", "name": "Channel"},
    "IMDB_POSTER": {"help": "Disable / Enable IMDB posters", "name": "IMDb Posters"},
    "PM_IMDB": {"help": "Enable or disable IMDB status in PM", "name": "PM IMDb Info"},
    "PM_IMDB_POSTER": {"help": "Disable / Enable IMDB posters in PM", "name": "PM IMDb Posters"},
    "DOWNLOAD_BUTTON": {"help": "Enable / disable download button", "name": "Download Button"},
    "PHOTO_FILTER": {"help": "Enable / disable photo filter", "name": "Photo Filter"},
    "VIDEO_FILTER": {"help": "Enable / disable VIDEO FILTER", "name": "VIDEO FILTER"},
    "SPELL_CHECK": {"help": "Enable / disable Spell Check", "name": "Spell Check"},
    "IS_BUTTON": {"help": "Enable / disable IS Button", "name": "IS Button"},

    "IS_EPISODES": {"help": "Enable / disable IS EPISODES", "name": "IS EPISODES"},
    "IS_YEARS": {"help": "Enable / disable IS YEARS", "name": "IS YEARS"},
    "IS_SEASONS": {"help": "Enable / disable IS SEASONS", "name": "IS SEASONS"},
    "IS_QUALITIE": {"help": "Enable / disable IS QUALITIE", "name": "IS QUALITIE"},
    "IS_SENDALL": {"help": "Enable / disable IS SENDALL", "name": "IS SENDALL"},
    "IS_LANGUAGES": {"help": "Enable / disable IS LANGUAGES", "name": "IS LANGUAGES"},
    "AUTO_DELETE": {"help": "5 Min / Off Auto Delete", "name": "Auto Delete"},
}



async def get_cap(settings, remaining_seconds, files, query, total_results, search):
    if settings["IMDB"]:
        IMDB_CAP = Cache.IMDB_CAP.get(query.from_user.id)
        if IMDB_CAP:
            cap = IMDB_CAP
            cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
            for file in files:
                cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
        else:
            if settings["IMDB"]:  # type: ignore
                imdb = await get_poster(search, file=(files[0])["file_name"])
            else:
                imdb = {}
            if imdb:

                cap = Config.TEMPLATE.format(  # type: ignore
                    query=search,
                    mention=query.from_user.mention,
                    remaining=remaining_seconds,
                    **imdb,
                    **locals(),
                )
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
            else:
                cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
                cap+="<b><u>🍿 Your Movie Files 👇</u></b>\n\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
    else:
        cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
        cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
        for file in files:
            cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
    return cap


async def get_cap2(settings, remaining_seconds, files, query, total_results, search):
    if settings["IMDB"]:
        IMDB_CAP2 = Cache.IMDB_CAP2.get(query.from_user.id)
        if IMDB_CAP2:
            cap = IMDB_CAP2
            cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
            for file in files:
                cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
        else:
            if settings["IMDB"]:  # type: ignore
                imdb = await get_poster(search, file=(files[0])["file_name"])
            else:
                imdb = {}
            if imdb:

                cap = Config.TEMPLATE.format(  # type: ignore
                    query=search,
                    mention=query.from_user.mention,
                    remaining=remaining_seconds,
                    **imdb,
                    **locals(),
                )
                cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
            else:
                cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
                cap+="<b><u>🍿 Your Movie Files 👇</u></b>\n\n"
                for file in files:
                    cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
    else:
        cap = f"○ **Query**:{search}\n○ **Total Results**: {total_results}\n○ **Request By**: {message.from_user.mention}\n○ **Result Show In**: `{remaining} seconds`"
        cap+="<b>\n\n○ <u>**🍿 Your Movie Files 👇**</u></b>\n"
        for file in files:
            cap += f"""<b>\n○ <a href="https://telegram.me/{Cache.U_NAME}?start=files_{file['file_id']}">{file['file_name']} [{get_size(file['file_size'])}]\n</a></b>"""
    return cap


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def broadcast_messages_group(chat_id, message):
    try:
        kd = await message.copy(chat_id=chat_id)
        try:
            await kd.pin()
        except:
            pass
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages_group(chat_id, message)
    except Exception as e:
        return False, "Error"


async def is_check_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

def get_file_id(msg: types.Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: types.Message) -> Union[int, str]:
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(Config.LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    tz = pytz.timezone('Asia/Yangon')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            return False
        else:
            return True
    else:
        return False


def get_status():
    tz = pytz.timezone('Asia/Yangon')
    hour = datetime.now(tz).time().hour
    if 5 <= hour < 12:
        sts = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ"
    elif 12 <= hour < 18:
        sts = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ"
    else:
        sts = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ"
    return sts

def get_time(seconds):
    result = ''
    days, remainder = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days} Days '
    hours, remainder = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours} Hours '
    minutes, seconds = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes} Minutes '
    seconds = int(seconds)
    if seconds != 0:
        result += f'{seconds} Seconds '
    if result == '':
        result += '-'
    return result.strip()


def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name} '
    return result.strip()

def b64_encode(s: str) -> str:

    return base64.urlsafe_b64encode(s.encode("ascii")).decode().strip("=")


def b64_decode(s: str) -> str:
    return (base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))).decode("ascii")


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id: str) -> str:
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref  # type: ignore


async def handle_next_back(data, offset=0, max_results=0):
    out_data = data[offset:][:max_results]
    total_results = len(data)
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = 0
    return out_data, next_offset, total_results, max_results

def get_size(size: int) -> str:
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)  # type: ignore
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0  # type: ignore
    return "%.2f %s" % (size, units[i])


def get_bool(current: bool) -> bool:
    if current == True:
        return False
    else:
        return True


def better_bool(key: bool) -> str:
    if key == True:
        return "Enabled"
    return "Disabled"


def get_buttons(settings: dict):
    BTN = []
    for config in CONFIGURABLE:
        BTN.append(
            [
                types.InlineKeyboardButton(
                    CONFIGURABLE[config]["name"], callback_data=f"settings_info#{config}"
                ),
                types.InlineKeyboardButton(
                    better_bool(settings.get(config, True)), callback_data=f"settings_set#{config}"
                ),
            ]
        )
    BTN.append(
        [
            types.InlineKeyboardButton(
                "Close", callback_data="close_data"
            ),
        ]
    )
    return BTN


async def parse_link(chat_id: int, msg_id: int) -> str:
    username = Cache.USERNAMES.get(chat_id)
    if username is None:
        try:
            chat = await Cache.BOT.get_chat(chat_id)
        except Exception as e:
            log.exception(e)
            username = ""
        else:
            username = chat.username if chat.username else ""  # type: ignore
        Cache.USERNAMES[chat_id] = username
    if username:
        return f"https://t.me/{username}/{msg_id}"
    return f"https://t.me/c/{(str(chat_id)).replace('-100', '')}/{msg_id}"


async def update_config():
    for config in CONFIGURABLE:
        value = await config_db.get_settings(config)
        if value is not None:
            setattr(Config, config, value)


async def format_buttons(files: list, channel: bool):
    if channel:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {file['file_name']}",
                    url=f'{(await parse_link(file["chat_id"], file["message_id"]))}',
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {file['file_name']}",
                    callback_data=f"file {file['_id']}",
                ),
            ]
            for file in files
        ]
    return btn


FORCE_TEXT = """🗣 မတ်‌ဆွေကြည့်ချင်တဲ့ဇာတ်ကားကို ပိုပေးဖိုအတွက် 👉🏻 Join Channel 👈🏻 က Join ထားဖိုလိုပါတယ်။ 
Channel လေးကို  Join ပြီးရင် 
🔄 Try Again 👈 Tap me လေးကို နှိပ်လိုက်ရင် 👌 ရပါပြီး။ 

@Movie_Zone_KP"""


async def check_fsub(bot: Client, message: types.Message, try_again: str = None, sendMsg: bool = True):  # type: ignore
    user = message.from_user.id
    try:
        member = await bot.get_chat_member(Config.FORCE_SUB_CHANNEL, user)
    except errors.UserNotParticipant:
        if sendMsg:
            invite_link = await bot.create_chat_invite_link(Config.FORCE_SUB_CHANNEL)
            btn = [
                [types.InlineKeyboardButton("Join Channel", url=invite_link.invite_link)],
            ]
            if try_again:
                btn.append(
                    [
                        types.InlineKeyboardButton(
                            "Try Again", url=f"https://t.me/{bot.me.username}?start={try_again}"
                        )
                    ]
                )
            await message.reply(FORCE_TEXT, reply_markup=types.InlineKeyboardMarkup(btn))
        return False
    else:
        if member.status in [enums.ChatMemberStatus.BANNED]:
            await message.reply("you are banned to use this bot :-/")
            return False
        return True


async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].strip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string.lower())

    if unit in ['s', 'sec', 'secs', 'second', 'seconds']:
        return value
    elif unit in ['min', 'mins', 'minute', 'minutes']:
        return value * 60
    elif unit in ['hour', 'hours', 'hr', 'hrs']:
        return value * 3600
    elif unit in ['day', 'days']:
        return value * 86400
    elif unit in ['month', 'months']:
        return value * 86400 * 30
    elif unit in ['year', 'years']:
        return value * 86400 * 365
    elif unit in ['lifetime']:
        return 86400 * 365 * 100
    else:
        return 0

async def get_mmks(mmk_string):
    plans = {
        "1day": 1500,
        "1days": 1500,
        "7day": 1500,
        "7days": 1500,
        "1month": 3000,
        "1months": 3000,
        "2month": 5000,
        "2months": 5000,
        "3month": 8000,
        "3months": 8000,
        "6month": 10000,
        "6months": 10000,
        "9month": 13000,
        "9months": 13000,
        "1year": 15000,
        "1years": 15000,
        "2years": 25000,
        "3years": 35000,
        "lifetime": 50000,
        "ʟɪғᴇᴛɪᴍᴇ": 50000
    }
    
    price = plans.get(mmk_string.lower().replace(" ", "").replace("ᴍᴏɴᴛʜ", "month").replace("ʏᴇᴀʀ", "year"), "Invalid plan")
    return price


async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if not movie:
        return None
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)
