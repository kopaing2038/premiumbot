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
ADMIN_ID = "1113630298"


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


async def send_videos(bot):
    skip = 60000  # Number of files to skip
    current = skip  # Start current at -skip to adjust for skipped files
    
    videos = collection.find().skip(skip) 
    for video in videos:
        file_id = video.get("file_id")  # Get the file_id from the MongoDB document
        file_name = video.get("file_name")

        # Check if the file already exists in the saved collection
        existing_file = savecollection.find_one({'$or': [{'file_id': file_id}, {'file_name': file_name}]})
        if existing_file:
            current += 1  # Increment the counter for each successfully processed file
            print(f"{file_name} is already saved in the database. Skipping...")

            if current % 200 == 0:
                print("200 files processed. Waiting for 30 seconds...")
                await bot.send_message(chat_id=ADMIN_ID, text=f"200 files processed. Waiting for 30 seconds...{current}")

                await asyncio.sleep(30)
            continue  # Skip this file and move to the next one

        if file_id:
            # Save and send file only if it's not a duplicate
            success, _ = await save_file(bot, file_name, file_id)

            if success:
                print(f"Successfully sent and saved file: {file_name}")
                await asyncio.sleep(3)  # Wait for 3 seconds only if the file was sent successfully
            else:
                print(f"Failed to send or save file: {file_name}")
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

