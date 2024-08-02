import logging, asyncio, time, pytz, re, os
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


TechKPBot.start()
loop = asyncio.get_event_loop()



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

