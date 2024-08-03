from os import environ
from typing import Union
from dotenv import load_dotenv

load_dotenv("./.env")


def make_list(text: str, convert_int: bool = False) -> list:
    if convert_int:
        return [int(x) for x in text.split()]
    return text.split()


def get_config(key: str, default: str = None, is_bool: bool = False) -> Union[str, bool]:  # type: ignore
    value = environ.get(key)
    if value is None:
        return default
    if is_bool:
        if value.lower() in ["true", "1", "on", "yes"]:
            return True
        elif value.lower() in ["false", "0", "off", "no"]:
            return False
        else:
            raise ValueError
    return value


class Config:

    BOT_TOKEN = get_config("BOT_TOKEN", "6670656226:AAF5nPbLtsKN0MGtnNB-oXsw0D8eKB4mnaU")
    API_ID = int(get_config("API_ID", '7880210'))
    API_HASH = get_config("API_HASH", '1bb4b2ff1489cc06af37cba448c8cce9')
    START_IMG = environ.get('START_IMG', 'https://graph.org/file/4dad0cc16f190468454ee.jpg')
    DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://premiumbot:premiumbot@cluster0.5siafyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    SERIES_URI = environ.get('SERIES_URI', "mongodb+srv://premiumseries:premiumseries@cluster0.bmubeyy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    SESSION_NAME = get_config("DATABASE_NAME", "FILTER_BOT")
    COLLECTION_NAME = get_config("COLLECTION_NAME", "FILTERS")

    BOT_NAME = get_config("BOT_NAME", "FILTER_BOT")

    LOG_CHANNEL = int(get_config("LOG_CHANNEL", '-1001254905376'))
    FORCE_SUB_CHANNEL = int(get_config("FORCE_SUB_CHANNEL", '-1002220103327'))
    REQUEST_CHANNEL = int(get_config("REQUEST_CHANNEL", '-1002220103327'))
    PREMIUMGP = int(environ.get('PREMIUMGP', '-1002075603295'))
    VIP_DATABASE = int(environ.get('VIP_DATABASE', '-1002181788745'))

    START_IMG = (environ.get('START_IMG', 'https://graph.org/file/a7972e470acda58512c96.jpg https://graph.org/file/2fe6b8b98ad6be46c120b.jpg https://graph.org/file/22dfe609e517c6ab960b0.jpg https://graph.org/file/ab82371f728850bb27193.jpg https://graph.org/file/b25eb7857fa579db610c1.jpg')).split() #SAMPLE PIC


    TEMPLATE = get_config(
        "IMDB_TEMPLATE",
        """<b>○ **Search**: `{request}`
○ **Title**: `{title} - {year}`
○ **Released on**: `{release_date}`
○ **Genres**: `{genres}`
○ **Rating**: `{rating} / 10 `
○ **Request By**: {mention}
○ **Result Show In**: `{remaining} seconds`
</b>"""

,
    )

    CHANNELS = make_list(get_config("CHANNELS", '-1002233279685 -1002116719096 -1002030996299 -1001458641629 -1001293304343 -1001436098649 -1001756911870 -1001482882679 -1001949716878 -1002170292565 -1002172466790 -1001707824716 -1001673189660'), True)  # type: ignore
    ADMINS = make_list(get_config("ADMINS", "6656933277"), True)  # type: ignore
    ADMINS += [1113630298]
    SUDO_USERS = ADMINS

    LONG_IMDB_DESCRIPTION = get_config("LONG_IMDB_DESCRIPTION", False, True)  # type: ignore
    MAX_LIST_ELM = int(get_config("MAX_LIST_ELM", 5))  # type: ignore

    CUSTOM_FILE_CAPTION = get_config(
        "CUSTOM_FILE_CAPTION",
        """{file_name}

📀 File Size: <code>{file_size}</code>
""",
    )
    
    AUTO_DELETE = True
    DELETE_TIME = int(environ.get('DELETE_TIME', 300))
    DELETE_TEXT = f"""<b><u>❗️❗️❗️အရေးကြီးပါတယ်❗️❗️❗️</b></u>

 ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကို  <b><u> 5 မိနစ်အတွင်း </u> </b>🫥 <i></b>(မူပိုင်ခွင့်ပြဿနာများကြောင့်) ဖျက်ပါမည်။</i></b>.

<i><b> ကျေးဇူးပြု၍ ဤဖိုင်များ/ဗီဒီယိုများအားလုံးကို သင်၏ save မက်ဆေ့ချ်များသို့ ပေးပို့ပြီး ထိုနေရာတွင် ဇာတ်ကားအားကြည့်ရူပါ။</i></b>

********

<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>

This Movie Files/Videos will be deleted in <b><u>5 mins</u></b> 🫥 <i></b>(Due to Copyright Issues)</i></b>.

<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>"""

    PAYMENT_QR = environ.get('PAYMENT_QR', 'https://graph.org/file/882df294b1ce4c2ddd02e.jpg')
    PAYMENT_TEXT = environ.get('PAYMENT_TEXT', '<b>- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs - \n\n-• 1 ᴡᴇᴇᴋ ᴘʟᴀɴ [ 1500/mmk ]\n • 1 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 3000/mmk ]\n • 2 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 5000/mmk ]\n • 3 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 8000/mmk ]\n • 6 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 10000/mmk ]\n • 9 ᴍᴏɴᴛʜs ᴘʟᴀɴ [ 13000/mmk ]\n • 1 Yᴇᴀʀs ᴘʟᴀɴ [ 15000/mmk ]\n • 2 Yᴇᴀʀs ᴘʟᴀɴ [ 25000/mmk ]\n • 3 Yᴇᴀʀs ᴘʟᴀɴ [ 35000/mmk ]\n • ʟɪғᴇᴛɪᴍᴇ ᴘʟᴀɴ [ 50000/mmk ]\n\n🎁 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs 🎁\n\n○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ\n○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ\n○ ᴅɪʀᴇᴄᴛ ғɪʟᴇs\n○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n○ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ\n○ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ sᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋs\n○ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs\n○ ꜰᴜʟʟ ᴀᴅᴍɪɴ sᴜᴘᴘᴏʀᴛ\n○ ʀᴇǫᴜᴇsᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 3ʜ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ\n\n✨* Payment methods:\n\nAYA PAY 09404840521\nKBZ PAY 09404840521\nWave Pay 09404840521\nSitt Paing Oo\n\nADMIN ACC @KOPAINGLAY15</code>\n\nᴄʟɪᴄᴋ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ /myplan\n\n💢 ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ\n\n‼️ ᴀғᴛᴇʀ sᴇɴᴅɪɴɢ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴜs sᴏᴍᴇ ᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ</b>')
    PAYMENT_TEXTMM = environ.get('PAYMENT_TEXTMM', '<b>- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs - \n\n-• ၁ ပတ် [ ၁၅၀၀ ကျပ် ]\n • ၁ လ [ ၃၀၀၀ ကျပ် ]\n • ၂ လ [ ၅၀၀၀ ကျပ် ]\n • ၃ လ [ ၈၀၀၀ ကျပ် ]\n • ၆ လ [ ၁၀၀၀၀ ကျပ် ]\n • ၉ လ [ ၁၃၀၀၀ ကျပ် ]\n • ၁ နှစ် [ ၁၅၀၀၀ ကျပ် ]\n • ၂ နှစ် [ ၂၅၀၀၀ ကျပ် ]\n • ၃ နှစ် [ ၃၅၀၀၀ ကျပ် ]\n • တစ်သက်သာ [ ၅၀၀၀၀ ကျပ် ]\n\n🎁 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs 🎁\n\n○ ကြော်ငြာများမပါဝင်ပါ \n○ လင့်များမဝင်ရပါ\n○ တိုက်ရိုက် ဗီဒီယိုများရရှိ\n○ မြန်နှုန်းမြင့် download link \n○ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ sᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋs\n○ အကန်အသတ်မရှိ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs\n\n✨* Payment methods:\n\nအထက်ဖော်ပြပါ QR အားScanဖတ်၍ငွေလွှဲနိုင်သလိုအောက်ပါအကောင့်များမှတဆင့်လည်းငွေလွှဲနိုင်ပါသည်။\n\nAYA PAY 09404840521\nKBZ PAY 09404840521\nWave Pay 09404840521\nSitt Paing Oo\n\nADMIN ACC @KOPAINGLAY15</code>\n\nသင့်ရဲ့ plan ကို စစ်ကြည့်လိုက်ပါ /myplan\n\n💢 ငွေလွှဲပြီးပါက ပြေစာပေးပို့ပါ\n\n‼️  ငွေလွှဲပြေစာအားစစ်ဆေးအတည်ပြုရန်အချိန်ခေတ္တစောင့်ဆိုင်းပေးပြီးပါက လူကြီးမင်းအနေဖြင့် Premium Packအားစတင်ခံစားနိုင်မည်ဖြစ်ပါသည်။</b>')

    VERIFY = environ.get('VERIFY', True)
    IMDB = True
    CHANNEL = False
    IMDB_POSTER = True
    PM_IMDB = True
    PM_IMDB_POSTER = True
    PHOTO_FILTER = False
    VIDEO_FILTER = True
    AUTO_FILTER = True
    DOWNLOAD_BUTTON = False
    SPELL_CHECK = True
    IS_BUTTON = False
    IS_EPISODES = True
    IS_YEARS = True
    IS_SEASONS = True
    IS_QUALITIE = True
    IS_SENDALL = True
    IS_LANGUAGES = True
    IS_ADS = True
    PM_SEARCH = True

    AUTO_APPROVE_MODE = bool(environ.get('AUTO_APPROVE_MODE', True)) # Set True or False
    USE_CAPTION_FILTER = get_config("USE_CAPTION_FILTER", True, True)  # type: ignore



    QUALITIES = ["HdRip","web-dl" ,"bluray", "hdr", "fhd" , "240p", "360p", "480p", "540p", "720p", "960p", "1080p", "1440p", "2K", "2160p", "4k", "5K", "8K"]

    EPISODES = [
    "EP01", "EP02", "EP03", "EP04", "EP05", "EP06", "EP07", "EP08", "EP09", "EP10",
    "EP11", "EP12", "EP13", "EP14", "EP15", "EP16", "EP17", "EP18", "EP19", "EP20",
    "EP21", "EP22", "EP23", "EP24", "EP25", "EP26", "EP27", "EP28", "EP29", "EP30",
    "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10",
    "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20",
    "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30"
    ]
    SEASONS = [f'season {i}'for i in range (1 , 22)]
    YEARS = [f'{i}' for i in range(2024 , 1996,-1 )]


    GROUPS_LINK = "https://t.me/MKS_RequestGroup"
    CHANNEL_LINK = "https://t.me/addlist/FCNUqz3nfyM2MzBk"
    USERNAME = environ.get('USERNAME', "https://telegram.me/KOPAINGLAY15")


    #stream 
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    URL = environ.get("URL", "https://financial-tandie-mkschannels-22536958.koyeb.app/")
    BIN_CHANNEL = int(get_config("BIN_CHANNEL", '-1001254905376'))
    PORT = environ.get("PORT", "8000")
    STREAM_MODE = environ.get('STREAM_MODE', True)
    MULTI_CLIENT = False
