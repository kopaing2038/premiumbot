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

PAYMENT_QR = os.environ.get('PAYMENT_QR', 'https://graph.org/file/882df294b1ce4c2ddd02e.jpg')


STATUS_TXT = """
👤 Total Users: <code>{}</code>"""

NEW_USER_TXT = """<b>#New_User 

≈ ɪᴅ:- <code>{}</code>
≈ ɴᴀᴍᴇ:- {}</b>"""


PAYMENT_TEXT = """မင်္ဂလာပါ  

1. English Series အတွက်က Lifetime ကိုမှ 4000 Kyats ပဲကျသင့်ပါမယ်။
English Series List
https://t.me/Serieslists

2. Thailand Series အတွက်က Lifetime ကိုမှ 3000 Kyats ပဲကျသင့်ပါမယ်။
Thailand Series List
https://t.me/ThaiSeries_MTS

3. Chinese Series အတွက်က Lifetime ကိုမှ 3000 Kyats ပဲကျသင့်ပါမယ်။ 
Chinese Series List
https://t.me/Chinese_Series_MCS

4. Anime & Animation အတွက်က Lifetime ကိုမှ 3000 Kyats ပဲကျသင့်ပါမယ်။ 
Anime & Animation List
https://t.me/Anime_Animation_Series
 
⭐️ ကြိုက်တဲ့ Series Channel 2 ခုကို Package Membership ဝင်ရင်တော့ Lifetime ကိုမှ 6000 Kyats ပဲ ကျသင့်ပါမယ်‌နော်။ (လူဦးရေကန့်သတ်ထားပါတယ်နော်။)

⭐️ ကြိုက်နှစ်သက်ရာ Series Channel 3 ခုအား Package Membership Lifetime ကိုမှ 10000 Kyats နဲ့ မန်ဘာဝင်မယ်ဆိုရင် Series Channel 1 ခု အပိုဝင်ခွင်ရမှာပါနော်။ (လူဦးရေကန့်သတ်ထားပါတယ်နော်။)
"""
