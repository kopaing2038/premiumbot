import logging, asyncio, time, pytz, re, os, math, json, random, base64, sys, requests
from pyrogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import errors, filters, types, Client
from motor.motor_asyncio import AsyncIOMotorClient
from vip.info import *
from vip.database.db import db


@Client.on_message(filters.command('stats'))
async def stats(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    users = await db.total_users_count()
    await message.reply_text(STATUS_TXT.format(users))    
    




@Client.on_message(filters.command("start") & filters.incoming)
async def key_start(client, message):
    user = message.from_user.mention
    
    # Check if user exists, if not, add to the database
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        #await client.send_message(LOG_CHANNEL, NEW_USER_TXT.format(message.from_user.id, user))
        
    if len(message.command) == 2 and message.command[1] == 'vip':
        btn = [             
            [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KPOWNER")],
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        await msg.reply_photo(
            photo=PAYMENT_QR,
            caption=PAYMENT_TEXT,
            reply_markup=reply_markup
        )
        return
    # Create the custom keyboard
    keyboard = ReplyKeyboardMarkup(
        [
            ["လက်ရှိတင်ထားပြီးသော VIP Series များ"],  # First row
            ["မန်ဘာကြေးဘယ်လောက်လဲ", "မန်ဘာကြေးသွင်းရန်အကောင့်"],  # Second row
            ["Korean Series & Movie Free ကြည့်ရန်"],
            ["Premium ဖြင့်ကြည့်ရန်"], # Third row
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
        price = PAYMENT_TEXT
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
        await message.reply_text("KBZ Pay\n\n<code> 09404840521</code> \nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")

    elif message.text == "AYA Pay":
        await message.reply_text("AYA Pay\n\n<code> 09404840521</code> \nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")  

    elif message.text == "Wave Pay":
        await message.reply_text("Wave Money Pay\n\n<code> 09681111552</code> \nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner")

    elif message.text == "Mytel Pay":
        await message.reply_text("Mytel Pay\n\n<code> 09681111552</code> \nSitt Paing Oo\n\nငွေလွဲပြီးရင် ဒီအကောင့်ကို 👇👇 Screenshot လေးပို့ပေးပါ @KPOwner") 

    elif message.text == "ငွေလွှဲပြီး ပြေစာပို့ရန် Admin အကောင့်":
        await message.reply_text("https://t.me/KPOwner")  

    elif message.text == "🔙 Back":
        keyboard = ReplyKeyboardMarkup(
            [ 
                ["လက်ရှိတင်ထားပြီးသော VIP Series များ"],  # First row
                ["မန်ဘာကြေးဘယ်လောက်လဲ", "မန်ဘာကြေးသွင်းရန်အကောင့်"],  # Third row (separated buttons)
                ["Korean Series & Movie Free ကြည့်ရန်"],
                ["Premium ဖြင့်ကြည့်ရန်"], # Third row
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

    elif message.text == "Premium ဖြင့်ကြည့်ရန်":
        keyboard = ReplyKeyboardMarkup(
            [ 
                ["လစဉ်ကြေးဘယ်လောက်လဲ"],  # First row
                ["ပြေစာပို့ရန် Admin အကောင့်"],
                ["နာမူနာ ကြည့်ရန်"],
                ["🔙 Back"]# Fourth row
            ],
            resize_keyboard=True  # Optional: Makes the keyboard smaller
        )
    
        await message.reply_text("လစဉ်ကြေးဖြင့် Bot ထဲတွင်မိမိနှစ်သက်ရာ ဇာတ်ကားအားရှာ‌ဖွေကြည့်ရူ့ရသော feature ဖြစ်ပါသည်။", reply_markup=keyboard)  

    elif message.text == "လစဉ်ကြေးဘယ်လောက်လဲ":
        price = """မင်္ဂလာပါ  

- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs - 

-• 1 ᴡᴇᴇᴋ ᴘʟᴀɴ [ 1500/mmk ]
 • 1 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 3000/mmk ]
 • 2 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 5000/mmk ]
 • 3 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 8000/mmk ]
 • 6 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 10000/mmk ]
 • 9 ᴍᴏɴᴛʜs ᴘʟᴀɴ [ 13000/mmk ]
 • 1 Yᴇᴀʀs ᴘʟᴀɴ [ 15000/mmk ]
 • 2 Yᴇᴀʀs ᴘʟᴀɴ [ 25000/mmk ]
 • 3 Yᴇᴀʀs ᴘʟᴀɴ [ 35000/mmk ]
 • ʟɪғᴇᴛɪᴍᴇ ᴘʟᴀɴ [ 50000/mmk ]

🎁 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs 🎁

○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ
○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ
○ ᴅɪʀᴇᴄᴛ ғɪʟᴇs
○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ
○ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ
○ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ sᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋs
○ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs
○ ꜰᴜʟʟ ᴀᴅᴍɪɴ sᴜᴘᴘᴏʀᴛ
○ ʀᴇǫᴜᴇsᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 3ʜ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ

✨* Payment methods:

AYA PAY <code>09404840521</code> 
KBZ PAY <code>09404840521</code> 

Wave Pay <code>09681111552</code> 
Mytel Pay <code>09681111552</code> 
Sitt Paing Oo

ADMIN ACC @KOPAINGLAY15

Premium Bot 
@DIANA_FILTERBOT

Premium Plan ကြည့်ရန်
https://telegram.me/DIANA_FILTERBOT?start=premium

Free Bot အသုံးပြုနည်း
https://t.me/MKSVIPLINK1/14
"""
        await message.reply_text(f"{price}") 

    elif message.text == "ပြေစာပို့ရန် Admin အကောင့်":
        await message.reply_text("https://t.me/KOPAINGLAY15")  

    elif message.text == "နာမူနာ ကြည့်ရန်":
        await message.reply_text("နာမူနာ video ကြည့်ရန်\n\nhttps://t.me/MKSVIPLINK1/15")  

#
