import datetime
import time
import asyncio
from pyrogram import Client, filters
from TechKP.database.db import db
from TechKP.config.config import Config
from TechKP.utils.botTools import broadcast_messages, broadcast_messages_group
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired

@Client.on_message(filters.command("premium_broadcast") & filters.user(Config.ADMINS))
async def premium_pm_broadcast(bot, message):
    b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message")
    try:
        users = await db.get_all_premium()
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await db.premium_users_count()
        done = 0
        blocked = 0
        deleted = 0
        failed = 0
        success = 0
        async for user in users:
            if 'id' in user:
                try:
                    pti, sh = await broadcast_messages(int(user['id']), b_msg)
                    if pti:
                        success += 1
                    elif pti == False:
                        if sh == "Blocked":
                            blocked += 1
                        elif sh == "Deleted":
                            deleted += 1
                        elif sh == "Error":
                            failed += 1
                except FloodWait as e:
                    print(f"FloodWait exception occurred: {e}")
                    await asyncio.sleep(e.x)
                except UserIsBlocked:
                    blocked += 1
                except PeerIdInvalid:
                    deleted += 1
                except ChatAdminRequired:
                    failed += 1
                except Exception as e:
                    print(f"Unhandled exception: {e}")
                    failed += 1

                done += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

            else:
                # Handle the case where 'id' key is missing in the user dictionary
                done += 1
                failed += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

    except Exception as e:
        print(f"General error: {e}")


        
@Client.on_message(filters.command("user_broadcast") & filters.user(Config.ADMINS))
async def pm_broadcast(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    try:
        users = await db.get_uall_user()
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await db.total_user_ucount()
        done = 0
        blocked = 0
        deleted = 0
        failed = 0
        success = 0
        async for user in users:
            if 'id' in user:
                try:
                    pti, sh = await broadcast_messages(int(user['id']), b_msg)
                    if pti:
                        success += 1
                    elif pti == False:
                        if sh == "Blocked":
                            blocked += 1
                        elif sh == "Deleted":
                            deleted += 1
                        elif sh == "Error":
                            failed += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    done -= 1  # Retry logic: do not count the failed attempt
                except Exception as e:
                    print(f"error: {e}")
                    failed += 1
                done += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
            else:
                done += 1
                failed += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    
        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    except Exception as e:
        print(f"error: {e}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(Config.ADMINS))
async def broadcast_group(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    groups = await db.get_all_chats()
    sts = await message.reply_text(
        text='Broadcasting your messages To Groups...'
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = 0

    success = 0
    async for group in groups:
        pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Error":
                failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")
        
