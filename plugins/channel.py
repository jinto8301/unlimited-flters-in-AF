import pyrogram
from pyrogram import Client, filters
from pyrogram.handlers import DeletedMessagesHandler

from info import CHANNELS
from database.ia_filterdb import save_file
from utils import temp

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.channel & media_filter & filters.incoming)    # & ~filters.edited
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)


@pyrogram.Client.on_deleted_messages()
async def del_media(client, message):
    try:
        print("Message Handler Msg_Id: " + str(message[0].id) + " Chat: " + str(message[0].chat.id))
    # invite_link = await bot.create_chat_invite_link(int(message[0].chat.id))
    # print(invite_link.invite_link)
        async for event in pyrogram.Client.get_chat_event_log(client, chat_id=str(message[0].chat.id)):
            print("event:" + event)
    except Exception as e:
        print(str(e))
    #
    # """Media Handler"""
    # for file_type in ("document", "video", "audio"):
    #     media = getattr(message, file_type, None)
    #     if media is not None:
    #         break
    # else:
    #     return

# DELETE_HANDLER = DeletedMessagesHandler(del_media, filters.channel & filters.group)
# temp.BOT.add_handler(DELETE_HANDLER)
