from pyrogram import Client, filters
import datetime
import time
from vip.database.db import db
from vip.info import ADMINS
from vip.utils import users_broadcast, get_readable_time, temp
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup 

lock = asyncio.Lock()




@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
        temp.USERS_CANCEL = True
       
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(bot, message):
    if lock.locked():
        return await message.reply('Currently broadcast processing, Wait for complete.')

    p = await message.reply('<b>Do you want pin this message in users?</b>', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    if msg.text == 'Yes':
        is_pin = True
    elif msg.text == 'No':
        is_pin = False
    else:
        await p.delete()
        return await message.reply_text('Wrong Response!')
    await p.delete()
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴜsᴇʀs ⌛️</b>')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    async with lock:
        async for user in users:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"Users broadcast Cancelled!\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")
                return
            sts = await users_broadcast(int(user['id']), b_msg, is_pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                btn = [[
                    InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#users')
                ]]
                await b_sts.edit(f"Users broadcast in progress...\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>", reply_markup=InlineKeyboardMarkup(btn))
        await b_sts.edit(f"Users broadcast completed.\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")

