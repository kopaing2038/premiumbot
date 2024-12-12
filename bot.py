import logging, asyncio, time, pytz, re, os, json
from datetime import datetime, date
from aiohttp import web
from pyrogram import __version__, filters, types
from pyrogram.raw.all import layer
from pyromod import listen
from pyrogram import Client, idle
from KPBOT.bot.clients import initialize_clients
from KPBOT.bot import TechKPBot
from TechKP.database.usersDb import usersDB
from TechKP.utils.cache import Cache
from TechKP.config.config import Config
from TechKP.utils.initialization import check_pending
from TechKP.utils.logger import LOGGER
from TechKP.plugins import web_server
from aiohttp import web
from KPBOT.util.keepalive import ping_server
from vip.bot import VIP
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

TechKPBot.start()
loop = asyncio.get_event_loop()



client = MongoClient(Config.DATABASE_URI)
db = client[Config.SESSION_NAME]
collection = db[Config.COLLECTION_NAME]

MONGO_URI = "mongodb+srv://msrpremium:msrpremium@cluster0.hhap4r4.mongodb.net/?retryWrites=true&w=majority"  # MongoDB server URI
saveclient = MongoClient(MONGO_URI)
savedb = saveclient[Config.SESSION_NAME]
savecollection = savedb[Config.COLLECTION_NAME]


CHANNEL_ID = "-1002491425774"



async def save_file(bot, file_name, file_id):
    """Save file in database, check for duplicates"""
    file = {
        'file_id': file_id,
        'file_name': file_name
    }
    try:
        # Try inserting the file into the saved collection
        savecollection.insert_one(file)
        
        # Validate and send video
        try:
            await bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=file_name)
            #print(f"{file_name} is successfully saved and sent.")
            return True, 1
        except ValueError:
            print(f"Invalid file ID: {file_id}. Skipping.")
            return False, 0
    except DuplicateKeyError:
        # File already exists in DB, skipping
        print(f"{file_name} is already saved in the database. Skipping.")
        return False, 0


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def send_videos(bot):
    videos = collection.find()  # Get all video documents from MongoDB
    current = 0  # Tracks the number of messages processed
    total_files = 0  # Tracks the number of saved files
    duplicate = 0  # Tracks duplicate files
    deleted = 0  # Tracks deleted messages
    no_media = 0  # Tracks non-media messages
    unsupported = 0  # Tracks unsupported files
    errors = 0  # Tracks errors
    
    remaining = collection.count_documents({})  
    for video in videos:
        file_id = video.get("file_id")  # Get the file_id from the MongoDB document
        file_name = video.get("file_name")
        
        # Check if the file already exists in the saved collection
        existing_file = savecollection.find_one({'$or': [{'file_id': file_id}, {'file_name': file_name}]})
        if existing_file:
            duplicate += 1
            print(f"{file_name} is already saved in the database. Skipping...")
            continue  # Skip this file and move to the next one

        if file_id:
            # Save and send file only if it's not a duplicate
            try:
                success, _ = await save_file(bot, file_name, file_id)
                if success:
                    total_files += 1
                    await asyncio.sleep(3)
            except Exception as e:
                errors += 1
                print(f"Error saving or sending file {file_name}: {e}")
        else:
            no_media += 1
            print(f"File ID not found for video: {video.get('file_name')}")

        current += 1
        remaining -= 1

        if current % 200 == 0:
            try:
                await bot.send_message(
                    text=(
                        f"Total messages fetched: <code>{current}</code>\n"
                        f"Total messages saved: <code>{total_files}</code>\n"
                        f"Remaining Messages: <code>{remaining}</code>\n"
                        f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                        f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                        f"Non-Media messages skipped: <code>{no_media + unsupported}</code>\n"
                        f"Errors Occurred: <code>{errors}</code>"
                    ),
                )
            except Exception as e:
                print(f"Error editing message text: {e}")



async def start():
    st = time.time()
    bot_info = await TechKPBot.get_me()
    me = bot_info
    print(f"{me.first_name} is started now ❤️")
    await initialize_clients()
    Cache.BANNED = await usersDB.get_banned_users()
    TechKPBot.loop.create_task(check_pending(TechKPBot))
    LOGGER(__name__).info(f"Banned Users list updated {Cache.BANNED}")
    LOGGER(__name__).info("Listening for updates from API..")

    me = bot_info
    Cache.ME = me.id
    Cache.BOT = TechKPBot
    Cache.U_NAME = me.username
    Cache.B_NAME = me.first_name
    Cache.B_LINK = me.mention
    Cache.BOT_START_TIME = time.time()
    tz = pytz.timezone('Asia/Yangon')
    today = date.today()
    now = datetime.now(tz)
    timee = now.strftime("%H:%M:%S %p") 
    
#    runner = web.AppRunner(await web_server())
   # await runner.setup()
  #  bind_address = "0.0.0.0"
  #  await web.TCPSite(runner, bind_address, PORT).start()
    await VIP.start()
    await send_videos(TechKPBot)
    await TechKPBot.send_message(
        chat_id=Config.LOG_CHANNEL,
        text=(
            f"<b>{me.mention} ʀᴇsᴛᴀʀᴛᴇᴅ 🤖\n\n"
            f"📆 ᴅᴀᴛᴇ - <code>{today}</code>\n"
            f"🕙 ᴛɪᴍᴇ - <code>{timee}</code>\n"
            f"🌍 ᴛɪᴍᴇ ᴢᴏɴᴇ - <code>Asia/Yangon</code></b>"
        )
    )
    
    tt = time.time() - st
    seconds = int(tt)
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, Config.PORT).start()

    for admin in Config.ADMINS:
        await TechKPBot.send_message(
            chat_id=admin,
            text=(
                f"<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ\n"
                f"🕥 ᴛɪᴍᴇ ᴛᴀᴋᴇɴ - <code>{seconds} sᴇᴄᴏɴᴅs</code></b>"
            )
        )

    await idle()






if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')

