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


TechKPBot.start()
loop = asyncio.get_event_loop()



client = MongoClient(Config.DATABASE_URI)
db = client[Config.SESSION_NAME]
collection = db[Config.COLLECTION_NAME]
LAST_SENT_FILE = "last_sent.json" 
CHANNEL_ID = "-1002491425774"

# Function to get the last sent video ID from file
def get_last_sent_video():
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, "r") as f:
            return json.load(f).get("last_sent_id", None)
    return None

# Function to save the last sent video ID to file
def save_last_sent_video(video_id):
    with open(LAST_SENT_FILE, "w") as f:
        json.dump({"last_sent_id": video_id}, f)

# Asynchronous function to send video to Telegram Channel
async def send_video_to_channel(file_path):
    try:
        await TechKPBot.send_video(chat_id=CHANNEL_ID, video=file_path)
        print(f"Video sent successfully: {file_path}")
    except Exception as e:
        print(f"Error sending video {file_path}: {e}")

# Asynchronous function to send all videos with a 3-second delay
async def send_videos():
    last_sent_id = get_last_sent_video()  # Get the ID of the last sent video
    videos = collection.find()  # Get all video documents from MongoDB
    
    # Flag to determine when to start sending videos
    start_sending = False

    # Loop through the videos in the collection
    for video in videos:
        video_id = str(video.get("_id"))
        
        # If the video ID matches the last sent ID, start sending from the next video
        if last_sent_id and video_id == last_sent_id:
            start_sending = True
            continue  # Skip the last sent video
        
        # Start sending only after the last sent video is found
        if start_sending:
            file_path = video.get("file_path")  # Assuming the file path is saved in MongoDB
            if file_path and os.path.exists(file_path):
                await send_video_to_channel(file_path)  # Send the video to the channel
                save_last_sent_video(video_id)  # Save the current video as the last sent video
                await asyncio.sleep(3)  # Wait for 3 seconds before sending the next video
            else:
                print(f"File path {file_path} not found or invalid.")
        else:
            # Skip videos before the last sent one
            continue


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
    await send_videos()
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

