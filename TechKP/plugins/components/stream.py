from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from TechKP.config.config import Config
from urllib.parse import quote_plus
from KPBOT.util.file_properties import get_name, get_hash, get_media_file_size
from KPBOT.util.human_readable import humanbytes
import humanize
import random


@Client.on_message(filters.command("stream") & filters.private)
async def stream_vip_start(client, message):
    if Config.STREAM_MODE == False:
        return 
    
    msg = await client.ask(message.chat.id, "**Now send me your file/video to get stream and download link**")
    if not msg.media:
        return await message.reply("**Please send me supported media.**")
    
    if msg.media in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
        file = getattr(msg, msg.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size) 
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention 

        log_msg = await client.send_cached_media(
            chat_id=Config.BIN_CHANNEL,
            file_id=fileid,
        )
        
        fileName = quote_plus(get_name(log_msg))
        stream = f"{Config.URL}watch/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
        download = f"{Config.URL}{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
 
        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                 InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]
            ])
        )
        
        rm = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                    InlineKeyboardButton('ᴅᴏᴡɴʟᴏᴀᴅ 📥', url=download)
                ]
            ]
        )
        
        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""
        
        await message.reply_text(
            text=msg_text.format(
                get_name(log_msg),
                humanbytes(get_media_file_size(msg)),
                download,
                stream
            ),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm
        )
