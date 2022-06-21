import asyncio
import os
import shutil

from info import *
from pyrogram import Client, filters
from telegraph import upload_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserNotParticipant


@Client.on_message(filters.command("telegraph") & filters.private)
async def getmedia(client, update):
    # if not await is_subscribed(client, update):
    #     try:
    #         invite_link = await client.create_chat_invite_link("UFSBotz")
    #     except ChatAdminRequired:
    #         print("Make Sure Bot Is Admin In Force Sub Channel")
    #         return
    #     btn = [
    #         [
    #             InlineKeyboardButton(
    #                 "🤖 Join Updates Channel", url=invite_link.invite_link
    #             )
    #         ]
    #     ]
    #     await client.send_message(
    #         chat_id=update.from_user.id,
    #         text="**Iғ Yᴏᴜ Wᴀɴᴛ Tᴏ Usᴇ Tʜɪs Bᴏᴛ, Yᴏᴜ Mᴜsᴛ Jᴏɪɴ Tʜᴇ Cʜᴀɴɴᴇʟ.\n"
    #              "Because I Am Providing You Completely Free To Use The Bot\n\n"
    #              "Please Join My Updates Channel To Use This Bot!**",
    #         reply_markup=InlineKeyboardMarkup(btn)
    #     )
    #     return

    org_message = update.reply_to_message
    medianame = TMP_DOWNLOAD_DIRECTORY + str(org_message.from_user.id)

    await update.delete()
    try:
        # await org_message.reply_chat_action("typing...")
        message = await org_message.reply_text(
            text="`⏳ Please Wait...`",
            quote=True,
            disable_web_page_preview=True
        )
        await asyncio.sleep(1)
        await client.download_media(
            message=org_message,
            file_name=medianame
        )
        response = upload_file(medianame)
        try:
            os.remove(medianame)
        except:
            pass
    except Exception as error:
        text = f"Error :- <code>{error}</code>"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton('More Help', callback_data='help')]]
        )
        await message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        return

    text = f"**Your Link :-** `https://telegra.ph{response[0]}`\n\n**Join Discussion Group:-** @UFSBotzSupport"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Open Link", url=f"https://telegra.ph{response[0]}"),
                InlineKeyboardButton(text="Share Link",
                                     url=f"https://telegram.me/share/url?url=https://telegra.ph{response[0]}")
            ],
            [
                InlineKeyboardButton(text="🤖 Join Updates Channel", url="https://telegram.me/UFSBotz")
            ]
        ]
    )

    await message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member("UFSBotz", query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        print(e)
    else:
        if user.status != 'kicked':
            return True

    return False


__help__ = """
 - /telegraph: Get Your Telegraph Link For Your Pics 
"""

__mod_name__ = "Telegraph"