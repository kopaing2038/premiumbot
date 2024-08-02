
from datetime import timedelta
from asyncio import sleep 
import pytz, math
import datetime, time
from TechKP.utils.botTools import get_seconds, get_status
from TechKP.database.db import db 
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
import traceback
from TechKP.config.Script import script
from TechKP.config.config import Config
from TechKP.utils.cache import Cache
from TechKP.utils.botTools import get_size, get_status, get_seconds, get_mmks, handle_next_back
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from pyrogram.errors import PeerIdInvalid

logging.basicConfig(level=logging.INFO)


@Client.on_message(filters.command("premium") & filters.user(Config.ADMINS))
async def add_premium(client, message):
    try:
        _, user_id, time, *custom_message = message.text.split(" ", 3)
        custom_message = "**Tʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴘᴜʀᴄʜᴀsɪɴɢ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴘᴀᴄᴋᴀɢᴇ. Nᴏᴡ, ʟᴇᴠᴇʀᴀɢᴇ ɪᴛs ғᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ**" if not custom_message else " ".join(custom_message)
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Yangon"))
        current_time = time_zone.strftime("%d-%m-%Y : %I:%M:%S %p")
        current_times = time_zone.strftime("%d-%m-%Y")
        user = await client.get_users(user_id)
        seconds = await get_seconds(time)
        mmks = await get_mmks(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + timedelta(seconds=seconds)
            user_data = {"_id": user.id, "prexdate": expiry_time.timestamp(), "expiry_time": expiry_time, "subscription_plan": time, "id": user.id} 
            await db.update_user(user_data)
            data = await db.get_user(user.id)
            expiry = data.get("expiry_time")
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Yangon")).strftime("%d-%m-%Y  :  %I:%M:%S %p")
            await message.reply_text(f"<b><u>Premium Access Added To The User</u>\n\n👤 User: {user.mention}\n\n🪪 User id: <code>{user_id}</code>\n\n⏰ Premium Access: {time}\n\n🎩 Joining : {current_time}\n\n⌛️ Expiry: {expiry_str_in_ist}.\n\n<code>{custom_message}</code></b>", disable_web_page_preview=True)
            await client.send_message(chat_id=user_id, text=f"<b>Dear {user.mention},\n\nYour payment for MKS & KP premium services has been successfully received.\n\nUser ID Number - {user_id}\nUser Name - {user.mention}\nProduct - {time}\nPaid Date - {current_times}\nPeriod - {current_time} to {expiry_str_in_ist}\nPayment Amount - {mmks}\n\nTo check your remaining subscription, type /myplan send it.\n\nThank you for choosing our services.\n\nMKS & KP Team\n\n@KOPAINGLAY15\n\n<code>{custom_message}</code></b>", disable_web_page_preview=True)
            await client.send_message(chat_id=user_id, text=f"<b>လေးစားရပါသော {user.mention} လူကြီးမင်းရှင့်\n\nMKS & KP မှ ပရီမီယံဝန်ဆောင်မှုအတွက် လူကြီးမင်း၏ငွေပေးချေမှုအား အောင်မြင်စွာ လက်ခံရရှိပါသည်။\n\nသုံးစွဲသူ အိုင်ဒီနံပါတ် - {user_id}\n\nသုံးစွဲသူ အမည် - {user.mention}\n\nဝန်ဆောင်မှု အမျိုးအစား - {time}\n\nငွေပေးသွင်းသည့်နေ့  - {current_times}\n\nအသုံးပြုနိုင်သည့်ကာလ - {current_time} မှ {expiry_str_in_ist} အထိ\n\nပေးသွင်းသည့် ပမာဏ  - {mmks} \n\nလူကြီးမင်းရဲ့သက်တမ်းလက်ကျန်ကို သိချင်ပါက /myplan ရိုက်ပို့ပါ။\n\nကျွန်ုပ်တို့ဝန်ဆောင်မှုအား ရွေးချယ်ခြင်းအတွက် ကျေးဇူးတင်ပါသည်။\n\nMKS & KP Team\n\n@KOPAINGLAY15</b>", disable_web_page_preview=True)
            #await client.send_message(chat_id=Config.PREMIUMGP, text=f"<b>လေးစားရပါသော {user.mention} လူကြီးမင်းရှင့်\n\nMKS & KP မှ ပရီမီယံဝန်ဆောင်မှုအတွက် လူကြီးမင်း၏ငွေပေးချေမှုအား အောင်မြင်စွာ လက်ခံရရှိပါသည်။\n\nသုံးစွဲသူ အိုင်ဒီနံပါတ် - {user_id}\n\nသုံးစွဲသူ အမည် - {user.mention}\n\nဝန်ဆောင်မှု အမျိုးအစား - {time}\n\nငွေပေးသွင်းသည့်နေ့  - {current_times}\n\nအသုံးပြုနိုင်သည့်ကာလ - {current_time} မှ {expiry_str_in_ist} အထိ\n\nပေးသွင်းသည့် ပမာဏ  - {mmks} \n\nလူကြီးမင်းရဲ့သက်တမ်းလက်ကျန်ကို သိချင်ပါက /myplan ရိုက်ပို့ပါ။\n\nကျွန်ုပ်တို့ဝန်ဆောင်မှုအား ရွေးချယ်ခြင်းအတွက် ကျေးဇူးတင်ပါသည်။\n\nMKS & KP Team\n\n@KOPAINGLAY15</b>", disable_web_page_preview=True)

            await client.send_message(Config.REQUEST_CHANNEL, text=f"#Added_Premium\n\n👤 User - {user.mention}\n\n🪪 User Id - <code>{user_id}</code>\n\n⏰ Premium Access - {time}\n\n🎩 Joining - {current_time}\n\n⌛️ Expiry - {expiry_str_in_ist}\n\n<code>{custom_message}</code>", disable_web_page_preview=True)
        else:
            await message.reply_text("<b>⚠️ Invalid Format, Use This Format - <code>/add_premium 1030335104 1day</code>\n\n<u>Time Format -</u>\n\n<code>1 day for day\n1 hour for hour\n1 min for minutes\n1 month for month\n1 year for year</code>\n\nChange As Your Wish Like 2, 3, 4, 5 etc....</b>")
    except ValueError:
        await message.reply_text("<b>⚠️ Invalid Format, Use This Format - <code>/add_premium 1030335104 1day</code>\n\n<u>Time Format -</u>\n\n<code>1 day for day\n1 hour for hour\n1 min for minutes\n1 month for month\n1 year for year</code>\n\nChange As Your Wish Like 2, 3, 4, 5 etc....</b>")
    except Exception as e:
        traceback.print_exc()
        await message.reply_text(f"error - {e}")

@Client.on_message(filters.command("plan"))
async def plans_cmd_handler(client, message): 
    user_id = message.from_user.id
    if message.from_user.username:
        user_info = f"@{message.from_user.username}"
    else:
        user_info = f"{message.from_user.mention}"
    log_message = f"<b><u>🚫 ᴛʜɪs ᴜsᴇʀs ᴛʀʏ ᴛᴏ ᴄʜᴇᴄᴋ /plan</u> \n\n {Cache.B_LINK}\n\n- ɪᴅ - `{user_id}`\n- ɴᴀᴍᴇ - {user_info}</b>"
    
    btn = [         
        [InlineKeyboardButton("Translate Myanmar", callback_data="translatemm")],    
        [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/KOPAINGLAY15")],
        [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=Config.PAYMENT_QR,
        caption=Config.PAYMENT_TEXT,
        reply_markup=reply_markup
    )
    await client.send_message(Config.LOG_CHANNEL, log_message)

@Client.on_message(filters.command("myplan"))
async def myplan(client, message):
    user = message.from_user.mention 
    user_id = message.from_user.id
    data = await db.get_user(message.from_user.id)
    if data and data.get("expiry_time"):
        expiry = data.get("expiry_time") 
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Yangon"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Yangon")).strftime("%d-%m-%Y  ⏰: %I:%M:%S %p")            
        current_time = datetime.datetime.now(pytz.timezone("Asia/Yangon"))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(f"#Premium_user_data:\n\n👤 User: {user}\n\n🪙 User Id: <code>{user_id}</code>\n\n⏰ Time Left: {time_left_str}\n\n⌛️ Expiry: {expiry_str_in_ist}.")   
    else:
        btn = [                                
            [InlineKeyboardButton('🤞🏻ɢᴇᴛ ʟᴏᴡ ᴘʀɪᴄᴇ ᴘʟᴀɴs 🍿', callback_data='plans')],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)         
        await message.reply_text(f"**Hey {user}.. 💔\n\nYou Do Not Have Any Active Premium Plans, If You Want To Take Premium Then Click on /plan To Know About The Plan\n\nသင်၏ Premium အစီအစဉ်တစ်ခုမှ မရှိသေးပါ။ Premium ယူလိုပါက /plan ကိုနှိပ်ပြီး အစီအစဉ်များကို ကြည့်ရှုနိုင်ပါသည်။**",reply_markup=reply_markup)
        
@Client.on_message(filters.command("remove_premium"))
async def remove_premium_cmd_handler(client, message):
    user_id = message.from_user.id
    if user_id not in Config.ADMINS:
        await message.delete()
        return
    if len(message.command) == 2:
        user_id = int(message.command[1])  # Convert the user_id to integer
      #  time = message.command[2]
        
        time = "60s"
        seconds = await get_seconds(time)
        try:
            if seconds > 0:
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                user_data = {"id": user_id, "prexdate": expiry_time.timestamp(), "expiry_time": expiry_time, "subscription_plan": time, "id": user_id} 
                await db.update_user(user_data)  # Use the update_user method to update or insert user data
                await message.reply_text(f"Premium access removed  to the user. {user_id}")
                await client.send_message(
                    chat_id=user_id,
                    text=f"<b>premium removed by admins \n\n Contact Admin if this is mistake \n\n 👮 Admin : @KOPAINGLAY15 \n</b>",                
                )
            else:
                await message.reply_text("Invalid time format.'")
        except Exception as e:
            await message.reply_text(f"Error: {e}")
        
    else:
        await message.reply_text("Usage: /remove_premium user_id")


client = AsyncIOMotorClient(Config.DATABASE_URI)
mydb = client[Config.SESSION_NAME]
dbcol = mydb["Premium_user"]


@Client.on_message(filters.command('removepremium') & filters.user(Config.ADMINS))
async def remove_admin_premium(bot, message):
    user_id = message.from_user.id
    msg = await message.reply("Please enter the user's ID to remove their premium subscription. \nType /cancel to cancel.")

    try:
        user_input = await bot.listen(user_id)
        if user_input.text == '/cancel':
            await user_input.delete()
            await msg.edit("Canceled this process.")
            return

        user_to_remove = user_input.text.strip()
        

        user_info = dbcol.find_one({"id": int(user_to_remove)})
        
        if user_info:
            dbcol.delete_one({"id": int(user_to_remove)})  # Delete the specific user by ID
            await message.reply(f"Premium subscription removed successfully for user {user_to_remove}.")
        else:
            await message.reply(f"No premium subscription found for user {user_to_remove}.")

        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error removing premium subscription: {str(e)}")


@Client.on_message(filters.command("check_plan") & filters.user(Config.ADMINS))
async def check_plan(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text("use this command with user id... like\n\n /check_plan user_id")
        return
    user_id = int(message.text.split(' ')[1])
    user_data = await db.get_user(user_id)

    if user_data and user_data.get("expiry_time"):
        expiry = user_data.get("expiry_time")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Yangon"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Yangon")).strftime("%d-%m-%Y %I:%M:%S %p")
        current_time = datetime.datetime.now(pytz.timezone("Asia/Yangon"))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        response = (
            f"User ID: {user_id}\n"
            f"Name: {(await client.get_users(user_id)).mention}\n"
            f"Expiry Date: {expiry_str_in_ist}\n"
            f"Expiry Time: {time_left_str}"
        )
    else:
        response = "User have not a premium..."
    await message.reply_text(response)


@Client.on_message(filters.command("premium_user") & filters.user(Config.ADMINS))
async def premium_user(client, message):
    aa = await message.reply_text("Fetching ...")  
    users = await db.get_all_premium()
    users_list = []
    async for user in users:
        users_list.append(user)    
    user_data = {user['id']: await db.get_user(user['id']) for user in users_list}    
    new_users = []
    for user in users_list:
        user_id = user['id']
        data = user_data.get(user_id)
        expiry = data.get("expiry_time") if data else None        
        if expiry:
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")          
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days, remainder = divmod(time_left.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, _ = divmod(remainder, 60)            
            time_left_str = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"            
            user_info = await client.get_users(user_id)
            user_str = (
                f"{len(new_users) + 1}. User ID: {user_id}\n"
                f"Name: {user_info.mention}\n"
                f"Expiry Date: {expiry_str_in_ist}\n"
                f"Expiry Time: {time_left_str}\n\n"
            )
            new_users.append(user_str)
    new = "Paid Users - \n\n" + "\n".join(new_users)   
    try:
        await aa.edit_text(new)
    except MessageTooLong:
        with open('usersplan.txt', 'w+') as outfile:
            outfile.write(new)
        await message.reply_document('usersplan.txt', caption="Paid Users:")


@Client.on_message(filters.command("bought") & filters.private)
async def bought(client, message):
    msg = await message.reply('Wait im checking...')
    replyed = message.reply_to_message
    if not replyed:
        await msg.edit("<b>Please reply with the screenshot of your payment for the premium purchase to proceed.\n\nFor example, first upload your screenshot, then reply to it using the '/bought' command</b>")
    if replyed and replyed.photo:
        await client.send_photo(
            photo=replyed.photo.file_id,
            chat_id=Config.REQUEST_CHANNEL,
            caption=f'<b>User - {message.from_user.mention}\nUser id - <code>{message.from_user.id}</code>\nusername - <code>{message.from_user.username}</code>\nUser Name - <code>{message.from_user.first_name}</code></b>',
            reply_markup=InlineKeyboardMarkup(
                [
                    
                    [
                        InlineKeyboardButton(
                            "Close", callback_data="close_data"
                        )
                    ]
                    
                ]
            )
        )
        await msg.edit_text('<b>Your screenshot has been sent to Admins</b>')


@Client.on_message(filters.private & filters.command('premium_users') & filters.user(Config.ADMINS))
async def premium_list_users(client, message):
    users, offset, total, max_btn = await handle_next_back(await db.get_premium_users(), max_results=30)
    if not users:
        return await message.reply('No users found.')
    if offset != 0:
        btn = [[
            InlineKeyboardButton(f"Page 1 / {math.ceil(total / max_btn)}", callback_data='bar'),
            InlineKeyboardButton('Next', callback_data=f"premium_next#{offset}")
        ]]
    else:
        btn = [[
            InlineKeyboardButton("Page 1 / 1", callback_data='bar')
        ]]
    text = ""
    for user_num, user in enumerate(users, start=1):
        try:
            user_info = await client.get_users(user['_id'])
            text += f"{user_num}. <a href='tg://user?id={user['_id']}'>{user_info.mention}</a> [<code>{user['_id']}</code>]\n\n"
        except PeerIdInvalid:
            logging.warning(f"Invalid user ID: {user['_id']}")
            text += f"{user_num}. <code>{user['_id']}</code> (Invalid ID)\n\n"
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btn))




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

@Client.on_message(filters.private & filters.command('free_users') & filters.user(Config.ADMINS))
async def free_list_users(client, message):
    users, offset, total, max_btn = await handle_next_back(await db.get_all_users(), max_results=30)
    if not users:
        return await message.reply('No users found.')
    if offset != 0:
        btn = [[
            InlineKeyboardButton(f"Page 1 / {math.ceil(total / max_btn)}", callback_data='bar'),
            InlineKeyboardButton('Next', callback_data=f"free_users_next#{offset}")
        ]]
    else:
        btn = [[
            InlineKeyboardButton("Page 1 / 1", callback_data='bar')
        ]]
    text = ""
    for user_num, user in enumerate(users, start=1):
        try:
            user_info = await client.get_users([user['_id']])
            text += f"{user_num}. <a href='tg://user?id={user['_id']}'>{user_info[0].mention}</a> [<code>{user['_id']}</code>]\n\n"
        except PeerIdInvalid:
            logging.warning(f"Invalid user ID: {user['_id']}")
            text += f"{user_num}. <code>{user['_id']}</code> (Invalid ID)\n\n"
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btn))

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
            user_info = await client.get_users([user['_id']])
            text += f"{user_num}. <a href='tg://user?id={user['_id']}'>{user_info[0].mention}</a> [<code>{user['_id']}</code>]\n\n"
        except PeerIdInvalid:
            logging.warning(f"Invalid user ID: {user['_id']}")
            text += f"{user_num}. <code>{user['_id']}</code> (Invalid ID)\n\n"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btn))
