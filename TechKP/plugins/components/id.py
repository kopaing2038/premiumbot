
import time
import random
from pyrogram import Client, filters, enums
import logging
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import asyncio
from telegraph import upload_file
from TechKP.utils.botTools import get_file_id



logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command('id'))
async def show_id(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"<b>» ᴜꜱᴇʀ ɪᴅ - <code>{message.from_user.id}</code></b>")

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"<b>» ɢʀᴏᴜᴘ ɪᴅ - <code>{message.chat.id}</code></b>")

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f"<b>» ᴄʜᴀɴɴᴇʟ ɪᴅ - <code>{message.chat.id}</code></b>")




CMD = ["/", "."]

@Client.on_message(filters.command("alive", CMD))
async def check_alive(_, message):
    await message.reply_text("**You are very lucky 🤞 I am alive ❤️ Press /start to use me**")


@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!\n{time_taken_s:.3f} ms")





@Client.on_message(filters.command(["json", 'js']))
async def jsonify(_, message):
    the_real_message = None
    reply_to_id = None
    pk = InlineKeyboardMarkup([[InlineKeyboardButton(text="𝙲𝙻𝙾𝚂𝙴", callback_data="close_data")]])  
                
    if message.reply_to_message:
        the_real_message = message.reply_to_message
    else:
        the_real_message = message

    try:        
        await message.reply_text(f"<code>{the_real_message}</code>", reply_markup=pk, quote=True)
    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))       
        await message.reply_document(
            document="json.text",
            caption=str(e),
            disable_notification=True,
            quote=True,
            reply_markup=reply_markup
        )            
        os.remove("json.text")


@Client.on_message(filters.command("written"))
async def create_file(c, message):
    content = message.reply_to_message.text
    file_name = message.text.split(" ", 1)[1]   
    try:
        with open(str(file_name), "w+") as out:
            out.write(str(content))       
        await message.reply_document(
            document=str(file_name),
            caption="out put file"
        )            
        os.remove(str(file_name))
    except Exception as e:
        await message.reply(e)



@Client.on_message(filters.command("stickerid") & filters.private)
async def stickerid(bot, message):
    s_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Sticker")
    if s_msg.sticker:
        await s_msg.reply_text(f"**Sticker ID is**  \n `{s_msg.sticker.file_id}` \n \n ** Unique ID is ** \n\n`{s_msg.sticker.file_unique_id}`")
    else: 
        await s_msg.reply_text("Oops !! Not a sticker file")


# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01



@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_upload(bot, update):
    t_msg = await bot.ask(chat_id = update.from_user.id, text = "Now Send Me Your Photo Or Video Under 5MB To Get Telegraph Link.")
  #  if not replied:
  #      await update.reply_text("𝚁𝙴𝙿𝙻𝚈 𝚃𝙾 𝙰 𝙿𝙷𝙾𝚃𝙾 𝙾𝚁 𝚅𝙸𝙳𝙴𝙾 𝚄𝙽𝙳𝙴𝚁 𝟻𝙼𝙱.")
 #       return
    file_info = get_file_id(t_msg)
    if not file_info:
        await update.reply_text("Not supported!")
        return
    text = await update.reply_text(text="<code>Downloading to My Server ...</code>", disable_web_page_preview=True)   
    media = await t_msg.download()   
    await text.edit_text(text="<code>Downloading Completed. Now I am Uploading to telegra.ph Link ...</code>", disable_web_page_preview=True)                                            
    try:
        response = upload_file(media)
    except Exception as error:
        print(error)
        await text.edit_text(text=f"Error :- {error}", disable_web_page_preview=True)       
        return    
    try:
        os.remove(media)
    except Exception as error:
        print(error)
        return    
    await text.edit_text(
        text=f"<b>Link :-</b>\n\n<code>https://graph.org{response[0]}</code>",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton(text="Open Link", url=f"https://graph.org{response[0]}"),
            InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url=https://graph.org{response[0]}")
            ],[
            InlineKeyboardButton(text="✗ Close ✗", callback_data="close")
            ]])
        )
    
