from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from TechKP.config.config import Config
from TechKP.utils.cache import Cache
from TechKP.config.Script import script
from TechKP.database.db import db
from datetime import datetime
import psutil
import time

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    check = [u.id for u in message.new_chat_members]
    if Cache.ME in check:
        if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
            total=await bot.get_chat_members_count(message.chat.id)
            user = message.from_user.mention if message.from_user else "Dear" 
            group_link = await message.chat.export_invite_link()
            await bot.send_message(Config.LOG_CHANNEL, script.NEW_GROUP_TXT.format(Cache.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user), disable_web_page_preview=True)  
            await db.add_chat(message.chat.id, message.chat.title)
            btn = [[
                InlineKeyboardButton('⚡️ sᴜᴘᴘᴏʀᴛ ⚡️', url=Config.GROUPS_LINK)
            ]]
            reply_markup=InlineKeyboardMarkup(btn)
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>☤ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ {message.chat.title}\n\n🤖 ᴅᴏɴ’ᴛ ꜰᴏʀɢᴇᴛ ᴛᴏ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ 🤖\n\n㊝ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ᴅᴏᴜʙᴛ ʏᴏᴜ ᴄʟᴇᴀʀ ɪᴛ ᴜsɪɴɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ㊜</b>",
                reply_markup=reply_markup
            )

@Client.on_message(filters.command('leave') & filters.user(Config.ADMINS))
async def leave_a_chat(bot, message):
    r = message.text.split(None)
    if len(message.command) == 1:
        return await message.reply('<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ʟɪᴋᴇ ᴛʜɪꜱ `/leave -100******`</b>')
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "ɴᴏ ʀᴇᴀꜱᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ..."
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        btn = [[
            InlineKeyboardButton('⚡️ ᴏᴡɴᴇʀ ⚡️', url=Config.USERNAME)
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await bot.send_message(
            chat_id=chat,
            text=f'😞 ʜᴇʟʟᴏ ᴅᴇᴀʀ,\nᴍʏ ᴏᴡɴᴇʀ ʜᴀꜱ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ ꜱᴏ ɪ ɢᴏ 😔\n\n🚫 ʀᴇᴀꜱᴏɴ ɪꜱ - <code>{reason}</code>\n\nɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ ᴛʜᴇɴ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴏᴡɴᴇʀ 👇',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await db.delete_chat(chat)
        await message.reply(f"<b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʟᴇꜰᴛ ꜰʀᴏᴍ ɢʀᴏᴜᴘ - `{chat}`</b>")
    except Exception as e:
        await message.reply(f'<b>🚫 ᴇʀʀᴏʀ - `{e}`</b>')

@Client.on_message(filters.command('groups') & filters.user(Config.ADMINS))
async def groups_list(bot, message):
    msg = await message.reply('<b>Searching...</b>')
    chats = await db.get_all_chats()
    out = "Groups saved in the database:\n\n"
    count = 1
    async for chat in chats:
        chat_info = await bot.get_chat(chat['id'])
        members_count = chat_info.members_count if chat_info.members_count else "Unknown"
        out += f"<b>{count}. Title - `{chat['title']}`\nID - `{chat['id']}`\nMembers - `{members_count}`</b>"
        out += '\n\n'
        count += 1
    try:
        if count > 1:
            await msg.edit_text(out)
        else:
            await msg.edit_text("<b>No groups found</b>")
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="<b>List of all groups</b>")

@Client.on_message(filters.command("invite") & filters.private & filters.user(Config.ADMINS))
async def invite(client, message):
    toGenInvLink = message.command[1]
    if len(toGenInvLink) != 14:
        return await message.reply("Invalid chat id\nAdd -100 before chat id if You did not add any yet.") 
    try:
        link = await client.export_chat_invite_link(toGenInvLink)
        await message.reply(link)
    except Exception as e:
        print(f'Error while generating invite link : {e}\nFor chat:{toGenInvLink}')
        await message.reply(f'Error while generating invite link : {e}\nFor chat:{toGenInvLink}')
