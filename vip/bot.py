from pyrogram import Client, __version__, filters
from datetime import date, datetime
import datetime
import pytz
from pyrogram import types
import time, os, asyncio
from vip.info import *


class Bot(Client):
    def __init__(self):
        super().__init__(
            name='dirrgect-bot_2',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            sleep_threshold=5,
            workers=150,
            plugins={"root": "vip/plugins"}
        )
        
    async def start(self):
        st = time.time()
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        print(f"{me.first_name} is started now ❤️")
        tz = pytz.timezone('Asia/Yangon')

        today = date.today()
        now = datetime.datetime.now(tz)
        timee = now.strftime("%H:%M:%S %p") 
        #await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} ʀᴇsᴛᴀʀᴛᴇᴅ 🤖\n\n📆 ᴅᴀᴛᴇ - <code>{today}</code>\n🕙 ᴛɪᴍᴇ - <code>{timee}</code>\n🌍 ᴛɪᴍᴇ ᴢᴏɴᴇ - <code>Asia/Yangon</code></b>")
        tt = time.time() - st
        seconds = int(datetime.timedelta(seconds=tt).seconds)
        for admin in ADMINS:
            await self.send_message(chat_id=admin, text=f"<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ\n🕥 ᴛɪᴍᴇ ᴛᴀᴋᴇɴ - <code>{seconds} sᴇᴄᴏɴᴅs</code></b>")
        await periodic_feed_update()


    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")
    


VIP = Bot()
