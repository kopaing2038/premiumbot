import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

API_ID = int(os.environ.get('API_ID', '7880210'))
API_HASH = os.environ.get('API_HASH', '1bb4b2ff1489cc06af37cba448c8cce9')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '1743843776:AAG9rf80SDC2LtWGkhSO47H50EVXrc-YMcI')


DATABASE_URI = os.environ.get('DATABASE_URI', "mongodb+srv://premiumbot:premiumbot@cluster0.5siafyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.environ.get('DATABASE_NAME', "VVIP_SERIES")

ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1113630298 6656933277').split()]
LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1001254905376'))
START_IMG = os.environ.get('START_IMG', 'https://l.arzfun.com/30hBn')




NEW_USER_TXT = """<b>#New_User 

≈ ɪᴅ:- <code>{}</code>
≈ ɴᴀᴍᴇ:- {}</b>"""
