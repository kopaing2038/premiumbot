from pyrogram import Client, filters
import datetime
import time
from vip.database.db import db
from vip.info import ADMINS

import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup 
from vip.utils import broadcast_messages, temp, get_readable_time

lock = asyncio.Lock()

               
@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("Trying to cancel users broadcasting...")
        temp.USERS_CANCEL = True
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("Trying to cancel groups broadcasting...")
               
@Client.on_message(filters.command(["broadcast", "pin_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def users_broadcast(bot, message):
    if lock.locked():
        return await message.reply('Currently broadcast processing, Wait for complete.')
    if message.command[0] == 'pin_broadcast':
        pin = True
    else:
        pin = False
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='Broadcasting your users messages...')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0

    async with lock:
        async for user in users:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"Users broadcast Cancelled!\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")
                return
            sts = await broadcast_messages(int(user['id']), b_msg, pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                btn = [[
                    InlineKeyboardButton('CANCEL', callback_data='broadcast_cancel#users')
                ]]
                await b_sts.edit(f"Users broadcast in progress...\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>", reply_markup=InlineKeyboardMarkup(btn))
        await b_sts.edit(f"Users broadcast completed.\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")

