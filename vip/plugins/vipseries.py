import logging, asyncio, time, pytz, re, os, math, json, random, base64, sys, requests
from pyrogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import errors, filters, types, Client
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URI = os.environ.get('DATABASE_URI', "mongodb+srv://premiumbot:premiumbot@cluster0.5siafyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1001254905376'))
START_IMG = os.environ.get('START_IMG', 'https://l.arzfun.com/30hBn')
NEW_USER_TXT = """<b>#New_User 

≈ ɪᴅ:- <code>{}</code>
≈ ɴᴀᴍᴇ:- {}</b>"""


client = AsyncIOMotorClient(DATABASE_URI)
mydb = client["VIPREGISTERBOT"]

class Database:
    def __init__(self):
        self.col = mydb.users


    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            point = 0,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )
db = Database()


@Client.on_message(filters.command("start") & filters.incoming)
async def key_start(client, message):
    user = message.from_user.mention
    
    # Check if user exists, if not, add to the database
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, NEW_USER_TXT.format(message.from_user.id, user))
        
    # Create the custom keyboard
    keyboard = ReplyKeyboardMarkup(
        [
            ["လက်ရှိတင်ထားပြီးသော VIP Series များ"],  # First row
            ["မန်ဘာကြေးဘယ်လောက်လဲ", "မန်ဘာကြေးသွင်းရန်အကောင့်"],  # Second row
            ["Korean Series & Movie Free ကြည့်ရန်"],  # Third row
            ["Admin Account"]  # Fourth row
        ],
        resize_keyboard=True  # Makes the keyboard smaller
    )
    
    # Send a message with the custom keyboard
    await message.reply_photo(
        photo=START_IMG,
        caption=f"""Hello {user} 🤗🤗 

မင်္ဂလာပါ 

VIP မန်ဘာဝင်ဖို့အတွက်သိချင်တာများကို တစ်ခုစီနှိပ်ကြည့်နိုင်ပါတယ်ခင်ဗျာ။

Owner - @KPOWNER""",
        reply_markup=keyboard
    )

@Client.on_message(filters.text & filters.incoming)
async def handle_buttons(client, message):
    user = message.from_user.mention
    if message.text == "လက်ရှိတင်ထားပြီးသော VIP Series များ":

        keyboard = ReplyKeyboardMarkup(
            [ 
                ["လက်ရှိကြည့်ရူ့နိုင်မည့် English Series များ။"],  # First row
                ["လက်ရှိကြည့်ရူ့နိုင်မည့် Chinese Series များ။"],  # Third row (separated buttons)
                ["လက်ရှိကြည့်ရူ့နိုင်မည့် Thailand Series များ။"],
                ["လက်ရှိကြည့်ရူ့နိုင်မည့် Anime & Animation Series များ။"] ,
                ["🔙 Back"]# Fourth row
            ],
            resize_keyboard=True  # Optional: Makes the keyboard smaller
        )
        # Send a message with the custom keyboard
        await message.reply_text("""လက်ရှိတင်ထားပြီးသော VIP Series များ""",
            reply_markup=keyboard
        )

    elif message.text == "လက်ရှိကြည့်ရူ့နိုင်မည့် Chinese Series များ။":
        await message.reply_text("Chinese VIP Series Member ဝင်ပြီးတာနဲ့ VIP Chinese Series List  တွင်ပါဝင်သောဇာတ်ကားများ အကုန်ကြည့်ရူနိုင်ပါသည်။ \n\nVIP Chinese Series List ရှိဇာတ်ကားများကို အောက်မှာကြည့်ပေးပါနော်။\n\nChinese Series List\nhttps://t.me/Chinese_Series_MCS")

    elif message.text == "လက်ရှိကြည့်ရူ့နိုင်မည့် Thailand Series များ။":
        await message.reply_text("Thailand VIP Series Member ဝင်ပြီးတာနဲ့ VIP Thailand Series List  တွင်ပါဝင်သောဇာတ်ကားများ အကုန်ကြည့်ရူနိုင်ပါသည်။ \n\nVIP Thailand Series List ရှိဇာတ်ကားများကို အောက်မှာကြည့်ပေးပါနော်။\n\nThailand Series List\nhttps://t.me/ThaiSeries_MTS")

    elif message.text == "လက်ရှိကြည့်ရူ့နိုင်မည့် Anime & Animation Series များ။":
        await message.reply_text("Anime & Animation VIP Series Member ဝင်ပြီးတာနဲ့ VIP Anime & Animation Series List  တွင်ပါဝင်သောဇာတ်ကားများ အကုန်ကြည့်ရူနိုင်ပါသည်။ \n\nVIP Anime & Animation Series List ရှိဇာတ်ကားများကို အောက်မှာကြည့်ပေးပါနော်။\n\nAnime & Animation Series List\nhttps://t.me/Anime_Animation_Series")

    elif message.text == "လက်ရှိကြည့်ရူ့နိုင်မည့် English Series များ။":
        await message.reply_text("English VIP Series Member ဝင်ပြီးတာနဲ့ VIP English Series List  တွင်ပါဝင်သောဇာတ်ကားများ အကုန်ကြည့်ရူနိုင်ပါသည်။ \n\nVIP English Series List ရှိဇာတ်ကားများကို အောက်မှာကြည့်ပေးပါနော်။\n\nEnglish Series List\nhttps://t.me/Serieslists")  # Replace with actual content



    elif message.text == "မန်ဘာကြေးဘယ်လောက်လဲ":
        price = """မင်္ဂလာပါ  

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
 
⭐️ ကြိုက်တဲ့ Series Channel 2 ခုကို Package Membership ဝင်ရင်တော့ Lifetime ကိုမှ 5000 Kyats ပဲ ကျသင့်ပါမယ်‌နော်။ (လူဦးရေကန့်သတ်ထားပါတယ်နော်။)

⭐️ ကြိုက်နှစ်သက်ရာ Series Channel 3 ခုအား Package Membership Lifetime ကိုမှ 9000 Kyats နဲ့ မန်ဘာဝင်မယ်ဆိုရင် Series Channel 1 ခု အပိုဝင်ခွင်ရမှာပါနော်။ (လူဦးရေကန့်သတ်ထားပါတယ်နော်။)
"""
        await message.reply_text(f"{price}") 


    elif message.text == "မန်ဘာကြေးသွင်းရန်အကောင့်":
        keyboard = ReplyKeyboardMarkup(
            [ 
                ["KBZ Pay", "AYA Pay"],  # First row
                ["Wave Pay", "Mytel Pay"],  # Third row (separated buttons)
                ["ငွေလွှဲပြီး ပြေစာပို့ရန် Admin အကောင့်"],
                ["🔙 Back"]# Fourth row
            ],
            resize_keyboard=True  # Optional: Makes the keyboard smaller
        )
    
        await message.reply_text("မန်ဘာကြေးသွင်းရန်အကောင့်များ", reply_markup=keyboard)  


    elif message.text == "Korean Series & Movie Free ကြည့်ရန်":
        await message.reply_text("Korean Series & Movie Free ကြည့်ရန် \n\nhttps://t.me/MKSVIPLINK1")

    elif message.text == "Admin Account":
        await message.reply_text("https://t.me/KPOwner")  

    elif message.text == "KBZ Pay":
        await message.reply_text("KBZ Pay\n\n09404840521\nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")

    elif message.text == "AYA Pay":
        await message.reply_text("AYA Pay\n\n09404840521\nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")  

    elif message.text == "Wave Pay":
        await message.reply_text("Wave Money Pay\n\n09681111552\nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")

    elif message.text == "Mytel Pay":
        await message.reply_text("Mytel Pay\n\n09681111552\nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner") 

    elif message.text == "ငွေလွှဲပြီး ပြေစာပို့ရန် Admin အကောင့်":
        await message.reply_text("https://t.me/KPOwner")  

    elif message.text == "🔙 Back":
        keyboard = ReplyKeyboardMarkup(
            [ 
                ["လက်ရှိတင်ထားပြီးသော VIP Series များ"],  # First row
                ["မန်ဘာကြေးဘယ်လောက်လဲ", "မန်ဘာကြေးသွင်းရန်အကောင့်"],  # Third row (separated buttons)
                ["Korean Series & Movie Free ကြည့်ရန်"],
                ["Admin Account"]                     # Fourth row
            ],
            resize_keyboard=True  # Optional: Makes the keyboard smaller
        )
    
        # Send a message with the custom keyboard
        await message.reply_photo(
            photo=START_IMG,
            caption=f"""Hello {user}🤗🤗 

မင်္ဂလာပါ 

VIP မန်ဘာဝင်ဖို့အတွက်သိချင်တာများကို တစ်ခုစီနှိပ်ကြည့်နိုင်ပါတယ်ခင်ဗျာ။

Owner - @KPOWNER""",
            reply_markup=keyboard
        )



#