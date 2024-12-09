import asyncio
import datetime
import time

from pyrogram import filters, types, Client

from ..config import Config
from ..database import configDB, usersDB
from ..utils.broadcastHelper import send_broadcast_to_user
from ..utils.cache import Cache
from ..utils.logger import LOGGER

LOG = LOGGER(__name__)

@Client.on_message(filters.command("broadcast") & filters.user(Config.SUDO_USERS))
async def broadcast_handler(bot: Client, msg: types.Message):
    is_copy = True
    is_pin = False
    __user = msg.chat.id

    await msg.reply("Alright, now send Photo / Video / Whatever you want.")
    b_msg = await bot.listen(msg.chat.id, timeout=600)
    if b_msg:
        if b_msg.text and b_msg.text == "/cancel":
            return await msg.reply("Cancelled")

    ask = await bot.send_message(
        msg.chat.id,
        "How do you want the message sent?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('Forward', callback_data='forward'),
                    types.InlineKeyboardButton("Copy", callback_data='copy')
                ]
            ]
        )
    )

    query = await bot.listen(msg.chat.id, filters=filters.callback_data, timeout=60)
    if query.data == "forward":
        is_copy = False
    await query.answer()

    to_broadcast = await b_msg.copy(Config.LOG_CHANNEL) if is_copy else await b_msg.forward(Config.LOG_CHANNEL)

    await ask.edit(
        "Do you want to pin the message?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('Yes', callback_data='pin'),
                    types.InlineKeyboardButton("No", callback_data='no')
                ]
            ]
        )
    )

    query = await bot.listen(msg.chat.id, filters=filters.callback_data, timeout=60)
    if query.data == "pin":
        is_pin = True
    await query.answer()

    await send_broadcast_to_user(msg.chat.id, to_broadcast, is_copy, is_pin)

    ask = await msg.reply(
        "Here is the sample. Do you wish to proceed?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('Yes', callback_data='yes'),
                    types.InlineKeyboardButton("No", callback_data='no')
                ]
            ]
        )
    )

    query = await bot.listen(msg.chat.id, filters=filters.callback_data, timeout=60)
    await query.answer()
    if query.data == "no":
        await msg.reply("Cancelled Broadcast Process")
        return

    sts = await msg.reply_text(
        text='Broadcasting your messages...',
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('Cancel', callback_data='broadcast_cancel')
                ]
            ]
        )
    )

    start_time = time.time()
    total_users = await usersDB.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0
    users_list = await usersDB.get_all_users()
    Cache.CANCEL_BROADCAST = False

    await configDB.update_config(
        'LAST_BROADCAST',
        {
            'id': to_broadcast.id,
            'settings': {"is_copy": is_copy, "is_pin": is_pin},
            'status': {'user_id': __user, 'msg_id': sts.id},
            'completed': False
        }
    )

    async for user in users_list:
        try:
            if Cache.CANCEL_BROADCAST:
                await sts.edit(
                    f"Broadcast Cancelled:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
                )
                Cache.CANCEL_BROADCAST = False
                await configDB.update_config(
                    'LAST_BROADCAST',
                    {
                        'id': to_broadcast.id,
                        'settings': {"is_copy": is_copy, "is_pin": is_pin},
                        'status': {'user_id': __user, 'msg_id': sts.id},
                        'completed': True
                    }
                )
                return

            user_id = int(user['id'])
            status_code, msg_id = await send_broadcast_to_user(user_id, to_broadcast, is_copy, is_pin)
            if status_code == 200:
                success += 1
                await usersDB.broadcast_id(user_id, to_broadcast.id)
                await usersDB.update_broadcast_msg(user_id, msg_id)
            elif status_code == 404:
                deleted += 1
            elif status_code == 302:
                blocked += 1
                await usersDB.add_to_pending(user_id, to_broadcast.id, {"is_copy": is_copy, "is_pin": is_pin})
                await usersDB.update_blocked(user_id, True)
            elif status_code == 400:
                failed += 1

            done += 1
            await asyncio.sleep(1)
            if not done % 20:
                await sts.edit(
                    f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}",
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [
                                types.InlineKeyboardButton('Cancel', callback_data='broadcast_cancel')
                            ]
                        ]
                    )
                )
        except Exception as e:
            LOG.exception(e)

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await configDB.update_config(
        'LAST_BROADCAST',
        {
            'id': to_broadcast.id,
            'settings': {"is_copy": is_copy, "is_pin": is_pin},
            'status': {'user_id': __user, 'msg_id': sts.id},
            'completed': True
        }
    )
    await sts.edit(
        f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
    )


@Client.on_callback_query(filters.regex(r'^broadcast_cancel') & filters.user(Config.SUDO_USERS))
async def cancel_broadcast(_: Client, query: types.CallbackQuery):
    await query.answer('Canceling...')
    Cache.CANCEL_BROADCAST = True
