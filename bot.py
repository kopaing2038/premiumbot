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
    # Check if the file already exists in the database based on file_id or file_name
    existing_file = savecollection.find_one({'$or': [{'file_id': file_id}, {'file_name': file_name}]})
    
    if existing_file:
        print(f"{file_name} is already saved in the database. Skipping...")
        return False, 0  # Return False as file is already in database
    
    # If not duplicate, proceed to save the file
    file = {
        'file_id': file_id,
        'file_name': file_name
    }
    try:
        savecollection.insert_one(file)
        #print(f"Attempting to send file: {file_name}")
        
        # Validate file_id before sending
        try:
            await bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=file_name)
            #print(f"{file_name} is successfully saved.")
            return True, 1
        except ValueError:
            print(f"Invalid file ID: {file_id}. Skipping.")
            return False, 0
            
    except DuplicateKeyError:
        print(f"{file_name} is already saved in the database. Skipping.")
        return False, 0  # File already exists in DB, skipping

# Function to get videos from MongoDB and send to channel
async def send_videos(bot):
    videos = collection.find()  # Get all video documents from MongoDB
    for video in videos:
        file_id = video.get("file_id")  # Get the file_id from the MongoDB document
        file_name = video.get("file_name")
        if file_id:
            await save_file(bot, file_name, file_id)  # Send the video to the channel
            await asyncio.sleep(3)  # Delay of 3 seconds between sending videos
        else:
            print(f"File ID not found for video: {video.get('file_name')}")


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

