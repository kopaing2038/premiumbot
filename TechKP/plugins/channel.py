
from ..config import Config
from pyrogram import Client, filters
from pyrogram.types import Message

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
    if file_type == "photo":
        media.file_name = message.caption
        media.mime_type = "image/jpg"
    media.caption = message.caption
    media.chat_id = message.chat.id
    media.message_id = message.id
    await a_filter.save_file(media)
