import os

class script(object):

    START_TXT = """<b> 🎭 <blockquote>Hᴇʟʟᴏ {}, ᴍʏ ɴᴀᴍᴇ <a href=https://t.me/{}>{}</a>  {} </blockquote>
    
ɪ ᴀᴍ【 ʟᴀᴛᴇꜱᴛ ᴀᴅᴠᴀɴᴄᴇᴅ 】ᴀɴᴅ ᴘᴏᴡᴇʀꜰᴜʟ ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ʙᴏᴛ+└ᴀᴡᴇꜱᴏᴍᴇ ꜰɪʟᴛᴇʀ┘ ᢾᴀɴᴅ ʙᴇꜱᴛ ᴜɪ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇᢿ</b>

<blockquote>ɪᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇ ᴀɪ ᴘᴏᴡᴇʀᴅ 🤖 ᴀᴜᴛᴏ ғɪʟᴛᴇʀ ʙᴏᴛ..
sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴏᴠɪᴇ ᴏʀ sᴇʀɪᴇs ɴᴀᴍᴇ ᴀɴᴅ sᴇᴇ ᴍʏ ᴍᴀɢɪᴄ..✨</blockquote>
<blockquote>ғᴏʀ ᴍᴏʀᴇ ᴅᴇᴛᴀɪʟs ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ 🤞🏻</blockquote>

ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : @KOPAINGLAY15</a>
</b>"""

    WELCOME_TEXT = """👋 Hello {mention} , ID : <code>{user_id}</code>\n\n Welcome to {title} group! 💞"""


    HELP_TXT = """<b>ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴅᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ꜱᴘᴇᴄɪꜰɪᴄ ᴍᴏᴅᴜʟᴇꜱ..</b>"""

    HELP_TEXT = """ရုပ်ရှင်ဇာတ်ကားများကို အလွယ်တကူရှာပြီးကြည့်ချင်တဲ့ မိတ်‌ဆွေများအတွက်  Premium Bot လေးပါ။အသုံးပြုပုံကတော့ အလွန်လွယ်ကူရိုးရှင်းပါတယ်ဗျ။ဇာတ်ကားနာမည်လေးပိုလိုက်တာနဲ့ Bot ‌ကရှာဖွေပေးပါမည်။

ယခု bot သည် premium user များသာ အသုံးပြုနိုင်သော bot ဖြစ်ပါသည်။ premium ဝင်မည်ဆိုပါက /plan လို ရိုက်ပို၍ ကြည့်ရှူနိုင်ပါသည်။ 

မရှိသော ဇာတ်ကားများတောင်းဆိုပါက 
#request ဇာတ်ကားနာမည်ထည့် ( #request Tha Roundup) ပြီး ရိုက်ပို၍ တောင်းဆိုနိုင်ပါသည်။"""

    USER_CMD_TXT = """<b>• /stats - 𝑡𝑜 𝑔𝑒𝑡 𝑠𝑡𝑎𝑡𝑢𝑠 𝑜𝑓 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝑑𝑏.
• /info - 𝑔𝑒𝑡 𝑢𝑠𝑒𝑟 𝑖𝑛𝑓𝑜
• /id - 𝑔𝑒𝑡 𝑡𝑔 𝑖𝑑𝑠.
• /imdb - 𝑓𝑒𝑡𝑐ℎ 𝑖𝑛𝑓𝑜 𝑓𝑟𝑜𝑚 𝑖𝑚𝑑𝑏.
• /search - 𝑇𝑜 𝑠𝑒𝑎𝑟𝑐ℎ 𝑓𝑟𝑜𝑚 𝑣𝑎𝑟𝑖𝑜𝑢𝑠 𝑠𝑜𝑢𝑟𝑐𝑒𝑠
• /start - 𝑇𝑜 𝑠𝑡𝑎𝑟𝑡 𝑡ℎ𝑒 𝑏𝑜𝑡
• /plan - 𝐶ℎ𝑒𝑐𝑘 𝑝𝑙𝑎𝑛 𝑑𝑒𝑡𝑎𝑖𝑙𝑠
• /myplan - 𝐶ℎ𝑒𝑐𝑘 𝑦𝑜𝑢𝑟 𝑝𝑙𝑎𝑛 𝑠𝑡𝑎𝑡𝑠
• /telegraph - 𝑔𝑒𝑡 𝑡𝑒𝑙𝑒𝑔𝑟𝑎𝑝ℎ 𝑙𝑖𝑛𝑘 𝑜𝑓 𝑎𝑛𝑦 𝑓𝑖𝑙𝑒 𝑢𝑛𝑑𝑒𝑟 5𝑚𝑏
• /stickerid - 𝑡𝑜 𝑔𝑒𝑡 𝑖𝑑 𝑎𝑛𝑑 𝑢𝑛𝑖𝑞𝑢𝑒 𝐼'𝑑 𝑜𝑓 𝑠𝑡𝑖𝑐𝑘𝑒𝑟
• /font - 𝑡𝑜 𝑔𝑒𝑡 𝑎𝑛𝑦 𝑡𝑦𝑝𝑒 𝑜𝑓 𝑓𝑜𝑛𝑡 𝑜𝑓 𝑎𝑛𝑦 𝑤𝑜𝑟𝑑
</b>"""

    ADMIN_CMD_TXT = """<b>
• /stats - 𝑡𝑜 𝑔𝑒𝑡 𝑠𝑡𝑎𝑡𝑢𝑠 𝑜𝑓 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝑑𝑏.
• /settings - 𝑇𝑜 𝑜𝑝𝑒𝑛 𝑠𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝑚𝑒𝑛𝑢
• /gsettings - 𝑇𝑜 𝑜𝑝𝑒𝑛 𝑠𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝑚𝑒𝑛𝑢
• /bsettings - 𝑇𝑜 𝑜𝑝𝑒𝑛 𝑠𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝑚𝑒𝑛𝑢
• /deleteall - 𝑑𝑒𝑙𝑒𝑡𝑒 𝑎𝑙𝑙 𝑖𝑛𝑑𝑒𝑥𝑒𝑑 𝑓𝑖𝑙𝑒𝑠.
• /delete - 𝑑𝑒𝑙𝑒𝑡𝑒 𝑎 𝑠𝑝𝑒𝑐𝑖𝑓𝑖𝑐 𝑓𝑖𝑙𝑒 𝑓𝑟𝑜𝑚 𝑖𝑛𝑑𝑒𝑥.
• /setskip - 𝑇𝑜 𝑠𝑘𝑖𝑝 𝑛𝑢𝑚𝑏𝑒𝑟 𝑜𝑓 𝑚𝑒𝑠𝑠𝑎𝑔𝑒𝑠 𝑤ℎ𝑒𝑛 𝑖𝑛𝑑𝑒𝑥𝑖𝑛𝑔 𝑓𝑖𝑙𝑒𝑠
• /users - 𝑡𝑜 𝑔𝑒𝑡 𝑙𝑖𝑠𝑡 𝑜𝑓 𝑚𝑦 𝑢𝑠𝑒𝑟𝑠 𝑎𝑛𝑑 𝑖𝑑𝑠.
• /chats - 𝑡𝑜 𝑔𝑒𝑡 𝑙𝑖𝑠𝑡 𝑜𝑓 𝑡ℎ𝑒 𝑚𝑦 𝑐ℎ𝑎𝑡𝑠 𝑎𝑛𝑑 𝑖𝑑𝑠 
• /leave  - 𝑡𝑜 𝑙𝑒𝑎𝑣𝑒 𝑓𝑟𝑜𝑚 𝑎 𝑐ℎ𝑎𝑡.
• /disable  -  𝑑𝑜 𝑑𝑖𝑠𝑎𝑏𝑙𝑒 𝑎 𝑐ℎ𝑎𝑡.
• /enable - 𝑟𝑒-𝑒𝑛𝑎𝑏𝑙𝑒 𝑐ℎ𝑎𝑡.
• /ban  - 𝑡𝑜 𝑏𝑎𝑛 𝑎 𝑢𝑠𝑒𝑟.
• /unban  - 𝑡𝑜 𝑢𝑛𝑏𝑎𝑛 𝑎 𝑢𝑠𝑒𝑟.
• /premium_broadcast - 𝑡𝑜 𝑏𝑟𝑜𝑎𝑑𝑐𝑎𝑠𝑡 𝑎 𝑚𝑒𝑠𝑠𝑎𝑔𝑒 𝑡𝑜 𝑎𝑙𝑙 𝑢𝑠𝑒𝑟𝑠
• /user_broadcast - 𝑡𝑜 𝑏𝑟𝑜𝑎𝑑𝑐𝑎𝑠𝑡 𝑎 𝑚𝑒𝑠𝑠𝑎𝑔𝑒 𝑡𝑜 𝑎𝑙𝑙 𝑢𝑠𝑒𝑟𝑠
• /grp_broadcast - 𝑇𝑜 𝑏𝑟𝑜𝑎𝑑𝑐𝑎𝑠𝑡 𝑎 𝑚𝑒𝑠𝑠𝑎𝑔𝑒 𝑡𝑜 𝑎𝑙𝑙 𝑐𝑜𝑛𝑛𝑒𝑐𝑡𝑒𝑑 𝑔𝑟𝑜𝑢𝑝𝑠.
• /premium - 𝐴𝑑𝑑 𝑢𝑠𝑒𝑟 𝑡𝑜 𝑝𝑟𝑒𝑚𝑖𝑢𝑚 𝑙𝑖𝑠𝑡
• /remove_premium - 𝑅𝑒𝑚𝑜𝑣𝑒 𝑢𝑠𝑒𝑟 𝑓𝑟𝑜𝑚 𝑝𝑟𝑒𝑚𝑖𝑢𝑚 𝑙𝑖𝑠𝑡
• /restart  - 𝑟𝑒𝑠𝑡𝑎𝑟𝑡 𝑡ℎ𝑒 𝑏𝑜𝑡 𝑠𝑒𝑟𝑣𝑒𝑟
• /purgerequests - 𝑑𝑒𝑙𝑒𝑡𝑒 𝑎𝑙𝑙 𝑗𝑜𝑖𝑛 𝑟𝑒𝑞𝑢𝑒𝑠𝑡𝑠 𝑓𝑟𝑜𝑚 𝑑𝑎𝑡𝑎𝑏𝑎𝑠𝑒
• /totalrequests - 𝑔𝑒𝑡 𝑡𝑜𝑡𝑎𝑙 𝑛𝑢𝑚𝑏𝑒𝑟 𝑜𝑓 𝑗𝑜𝑖𝑛 𝑟𝑒𝑞𝑢𝑒𝑠𝑡 𝑓𝑟𝑜𝑚 𝑑𝑎𝑡𝑎𝑏𝑎𝑠𝑒

</b>"""

    EXTRAMOD_TXT = """ʜᴇʟᴘ: Exᴛʀᴀ Mᴏᴅᴜʟᴇs
<b>ɴᴏᴛᴇ:</b>
my features Stay here new features coming soon...  
 <b>✯ Maintained by : <a href=https://t.me/KingVj01>☢VJ☢</a></b>
  
 <b>✯ Join here : <a href=https://t.me/vj_bots>☢Join my updateds☢</a></b> 
  
 ./id - <code>ɢᴇᴛ ɪᴅ ᴏꜰ ᴀ ꜱᴘᴇᴄɪꜰɪᴇᴅ ᴜꜱᴇʀ.</ 
 code> 
  
 ./info  - <code>ɢᴇᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ᴜꜱᴇʀ.</code> 
  
 ./telegraph - <code>Telegraph generator sen under 5MB video or photo I give telegraph link</code> 

./font - This command usage stylish and cool font generator [<code>example /font hi</code>]"""

    TELE_TXT = """<b>/telegraph - sᴇɴᴅ ᴍᴇ ᴘɪᴄᴛᴜʀᴇ ᴏʀ ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ (5ᴍʙ)

ɴᴏᴛᴇ - ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋ ɪɴ ʙᴏᴛʜ ɢʀᴏᴜᴘs ᴀɴᴅ ʙᴏᴛ ᴘᴍ</b>"""

    FONT_TXT= """<b>ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴍᴏᴅᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜰᴏɴᴛs sᴛʏʟᴇ, ᴊᴜsᴛ sᴇɴᴅ ᴍᴇ ʟɪᴋᴇ ᴛʜɪs ꜰᴏʀᴍᴀᴛ

<code>/font hi how are you</code></b>"""

    ABOUT_TEXT = """<b>🎭 ᴊᴀɪ sʜʀᴇᴇ ᴋʀɪsʜɴᴀ {},
    
🤖 ɪ'ᴍ <a href=https://t.me/{}</a> 
⚙️ ᴄʜɪʟʟɪɴɢ ᴏɴ : <a href="https://www.heroku.com/">ʜᴇʀᴏᴋᴜ</a>
🍿 ʙʀᴀɪɴ ғᴜᴇʟᴇᴅ : <a href="https://www.mongodb.com/">ᴍᴏɴɢᴏ ᴅʙ</a>
🐍 ᴄᴏᴅɪɴɢ ᴍᴜsᴄʟᴇs : <a href="https://www.python.org/">ᴘʏᴛʜᴏɴ 3</a>
😚 ᴍʏ ᴛʀᴜsᴛʏ sᴛᴇᴇᴅ: <a href="https://github.com/Mayuri-Chan/pyrofork">ᴘʏʀᴏғᴏʀᴋ</a>
🙏🏻 ᴍʏ ᴄʀᴇᴀᴛᴏʀ : <a href="https://telegram.me/KOPAINGLAY15">ᴋᴏ ᴘᴀɪɴɢ</a>
🤡 ᴍʏ ᴍᴀɴᴀɢᴇʀ : <a href="https://telegram.me/KOPAINGLAY15">ᴋᴘ</a>
🧑🏻‍💻 ʀᴇᴘᴏ : <a href="https://telegram.me/KOPAINGLAY15">ʟɪɴᴋ</a>
</b>"""


    OWNER_TXT = """ 
special Thanks To ❤️ Developers -

-Dev 1 [Owner of this bot ]<a href='https://t.me/KOPAINGLAY15'>Ko Paing</a>

-Dev 2 <a href='https://t.me/KPDeveloper'>KP</a>

"""


    I_CUDNT = """🤧 𝗛𝗲𝗹𝗹𝗼 {}

𝗜 𝗰𝗼𝘂𝗹𝗱𝗻'𝘁 𝗳𝗶𝗻𝗱 𝗮𝗻𝘆 𝗺𝗼𝘃𝗶𝗲 𝗼𝗿 𝘀𝗲𝗿𝗶𝗲𝘀 𝗶𝗻 𝘁𝗵𝗮𝘁 𝗻𝗮𝗺𝗲.. 😐"""

    CUDNT_FND = """🤧 𝗛𝗲𝗹𝗹𝗼 {}

𝗜 𝗰𝗼𝘂𝗹𝗱𝗻'𝘁 𝗳𝗶𝗻𝗱 𝗮𝗻𝘆𝘁𝗵𝗶𝗻𝗴 𝗿𝗲𝗹𝗮𝘁𝗲𝗱 𝘁𝗼 𝘁𝗵𝗮𝘁 𝗱𝗶𝗱 𝘆𝗼𝘂 𝗺𝗲𝗮𝗻 𝗮𝗻𝘆 𝗼𝗻𝗲 𝗼𝗳 𝘁𝗵𝗲𝘀𝗲 ?? 👇"""


    NO_RESULT_TXT = """<b>ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ʀᴇʟᴇᴀsᴇᴅ ᴏʀ ᴀᴅᴅᴇᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ 🙄</b>"""


    ALRT_TXT = f"⚠️ ʜᴇʟʟᴏ ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ..."

    OLD_ALRT_TXT = """ʏᴏᴜ ᴀʀᴇ ᴜsɪɴɢ ᴍʏ ᴏʟᴅ ᴍᴇssᴀɢᴇs..sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ.."""

    NEW_GROUP_TXT = """#New_Group {}

Group name - {}
Id - <code>{}</code>
Group username - @{}
Group link - {}
Total members - <code>{}</code>
User - {}"""

    REQUEST_TXT = """<b>📜 ᴜꜱᴇʀ - {}
📇 ɪᴅ - <code>{}</code>

🎁 ʀᴇǫᴜᴇꜱᴛ ᴍꜱɢ - <code>{}</code></b>"""  

    LOG_TEXT_P = """#NewUser

Bot = @{}
ID - <code>{}</code>
Nᴀᴍᴇ - {}"""


    PREMIUM_TEXT = """<b>👋 Hey There,
    
    <u>Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs</u> 🎁
    
○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ
○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ
○ ᴅɪʀᴇᴄᴛ ғɪʟᴇs
○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ
○ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ
○ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇʀ sᴛʀᴇᴀᴍɪɴɢ ʟɪɴᴋs
○ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs
○ ꜰᴜʟʟ ᴀᴅᴍɪɴ sᴜᴘᴘᴏʀᴛ
○ ʀᴇǫᴜᴇsᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 3ʜ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ
•────•────────•────•

➥ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ /myplan
‼️ ᴄʟɪᴄᴋ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴄʜᴇᴄᴋ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs & ɪᴛ's ᴘʀɪᴄᴇs</b>"""

    BUY_PLAN = """<b>○ <u>ғɪʀsᴛ sᴛᴇᴘ</u> : ᴘᴀʏ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴘʟᴀɴ ᴛᴏ ᴛʜɪs.

AYA PAY 09404840521
KBZ PAY 09404840521
Sitt Paing Oo

Wave Pay 09404840521
U Win
    
ADMIN ACC @KOPAINGLAY15

○ <u>secoɴᴅ sᴛᴇᴘ</u> : ᴛᴀᴋᴇ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ᴀɴᴅ sʜᴀʀᴇ ɪᴛ ᴅɪʀᴇᴄᴛʟʏ ʜᴇʀᴇ: {} 

○ <u>ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ sᴛᴇᴘ</u> : ᴏʀ ᴜᴘʟᴏᴀᴅ ᴛʜᴇ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴇʀᴇ ᴀɴᴅ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ /bought ᴄᴏᴍᴍᴀɴᴅ.

Yᴏᴜʀ <ul>ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ</ul> ᴡɪʟʟ ʙᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴀғᴛᴇʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ</b>

💢 ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ
‼️ ᴀғᴛᴇʀ sᴇɴᴅɪɴɢ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴜs sᴏᴍᴇ ᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ
"""


    PLAN_TEXT = """<b>ᴡᴇ ᴀʀᴇ ᴘʀᴏᴠɪᴅɪɴɢ ᴘʀᴇᴍɪᴜᴍ ᴀᴛ ᴛʜᴇ ʟᴏᴡᴇsᴛ ᴘʀɪᴄᴇs:
    
• 1 ᴡᴇᴇᴋ ᴘʟᴀɴ [ 1500/mmk ]
• 1 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 3000/mmk ]
• 2 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 5000/mmk ]
• 3 ᴍᴏɴᴛʜ ᴘʟᴀɴ [ 8000/mmk ]

ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ʙᴜʏɪɴɢ ↡↡↡
</b>"""



    STATUS_TXT = """<b>Tᴏᴛᴀʟ Fɪʟᴇs Fʀᴏᴍ Bᴏᴛʜ DBs: <code>{}</code>

<blockquote>Bᴏᴛ Usᴇʀs ᴀɴᴅ Cʜᴀᴛs Cᴏᴜɴᴛ</blockquote>
★ Pʀᴇᴍɪᴜᴍ Usᴇʀs: <code>{}</code>
★ Tᴏᴛᴀʟ Usᴇʀs: <code>{}</code>
★ Tᴏᴛᴀʟ Cʜᴀᴛs: <code>{}</code>

<blockquote>Pʀɪᴍᴀʀʏ Dᴀᴛᴀʙᴀsᴇ Sᴛᴀᴛɪsᴛɪᴄs</blockquote>
★ Tᴏᴛᴀʟ Fɪʟᴇs: <code>{}</code>
★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ: <code>{} MB</code>
★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ: <code>{} MB</code>

<blockquote>Sᴇᴄᴏɴᴅᴀʀʏ Dᴀᴛᴀʙᴀsᴇ Sᴛᴀᴛɪsᴛɪᴄs</blockquote>
★ Tᴏᴛᴀʟ Fɪʟᴇs: <code>{}</code>
★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ: <code>{} MB</code>
★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ: <code>{} MB</code>

<blockquote>Bᴏᴛ ᴀɴᴅ OS Sᴛᴀᴛɪsᴛɪᴄs</blockquote>
★ Cᴘᴜ: <code>{} %</code>
★ Sᴛᴏʀᴀɢᴇ: <code>{} / {}</code>
★ Rᴀᴍ: <code>{} / {}</code>
★ Bᴏᴛ Uᴘᴛɪᴍᴇ: <code>{}</code>
★ OS Uᴘᴛɪᴍᴇ: <code>{}</code>

★ Maintained by : @KPDeveloper

</b>"""
