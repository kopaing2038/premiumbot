
from ..config import Config
from pyrogram.types import Message
import asyncio
import re
from pyrogram import enums, filters, types
from pyrogram.errors import (ChannelInvalid, UsernameInvalid,
                             UsernameNotModified)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import types, enums, filters, Client
from ..database import a_filter

media_filter = filters.document | filters.video | filters.audio | filters.photo


@Client.on_message(filters.chat(Config.CHANNELS) & media_filter)  # type: ignore
async def media(bot: Client, message: Message):
    """Media Handler"""
    for file_type in ("document", "video", "audio", "photo"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    if message.media == enums.MessageMediaType.PHOTO:
        media.file_type = "photo"
        media.file_name = message.caption.split('\n')[0] if message.caption else ""
        media.mime_type = "image/jpg"
    elif message.media == enums.MessageMediaType.VIDEO:
        media.file_type = "video"
        media.file_name = message.video.file_name if message.caption else ""
        media.mime_type = "video/mp4"
    elif message.media == enums.MessageMediaType.AUDIO:
        media.file_type = "audio"
        media.file_name = message.audio.file_name if message.caption else ""
        media.mime_type = message.audio.mime_type if message.audio.mime_type else "audio/mpeg"
    elif message.media == enums.MessageMediaType.DOCUMENT and message.document is not None:
        media.file_type = "document"
        media.file_name = message.document.file_name if message.document.file_name else ""
        media.mime_type = message.document.mime_type if message.document.mime_type else ""
                
    media.caption = message.caption if message.caption else ""
    media.chat_id = message.chat.id
    media.channel_name = message.chat.username or message.chat.title
    media.message_id = message.id
    await a_filter.save_file(media)
