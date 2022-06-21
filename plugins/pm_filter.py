import json
import os
import re
import ast
import asyncio
import logging
import random
import pyrogram

from info import *
from Script import script
from pyrogram import Client, filters
from database.users_chats_db import db
from plugins.misc import paginate_modules
from plugins.helper_func import TimeFormatter
from database.filters_mdb import del_all, find_filter, get_filters
from utils import get_size, is_subscribed, get_poster, search_gagala, temp
from database.ia_filterdb import Media, get_file_details, get_search_results
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, BadRequest
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from database.settings_db import sett_db
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
BATCH_FILES = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)    # & ~filters.edited
async def give_filter(client, message):
    group_id = message.chat.id
    chat_type = message.sender_chat.type if message.sender_chat else message.chat.type
    name = message.text

    if chat_type.name in ["CHANNEL"]:
        text = f"""
#DETECT_SENDER_AS_CHANNEL

**CHANNEL: {message.sender_chat.title} ({message.sender_chat.id})** 
`CHAT: {message.chat.title} ({message.chat.id})`
**MESSAGE: You Cannot Request Via Channel**"""
        chat_channel = await message.reply_text(text, quote=True)
        await asyncio.sleep(5)
        await chat_channel.delete()
        await message.delete()
        return

    if len(message.text) < 1:
        try:
            msg = await message.reply_text(
                f"**Nice Try! But, I Need Minimum --__3__-- Character To Find Your Requesting Details,\n"
                f"Please Edit Your Request** `{message.text}`", quote=True)
            req = message.from_user.id if message.from_user else 0
            if temp.TEMP_USER.get(req):
                del temp.TEMP_USER[req]
            temp.TEMP_USER[req] = "edit"
            await asyncio.sleep(10)
            await msg.delete()
            return
        except Exception as e:
            logging.info(f"Error: \n{str(e)}")
            return

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            await check_manual_filter(client, group_id, keyword, message, 0)
            return
            # reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            #
            # if reply_text:
            #     reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")
            #
            # if btn is not None:
            #     try:
            #         if fileid == "None":
            #             if btn == "[]":
            #                 await message.reply_text(reply_text, disable_web_page_preview=True)
            #             else:
            #                 button = eval(btn)
            #                 await message.reply_text(
            #                     reply_text,
            #                     disable_web_page_preview=True,
            #                     reply_markup=InlineKeyboardMarkup(button)
            #                 )
            #         elif btn == "[]":
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or ""
            #             )
            #         else:
            #             button = eval(btn)
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or "",
            #                 reply_markup=InlineKeyboardMarkup(button)
            #             )
            #     except Exception as e:
            #         logger.exception(e)
            #     break


@Client.on_edited_message(filters.group & filters.text & filters.incoming)    # & filters.edited
async def give_filter_edited(client, message):
    group_id = message.chat.id
    chat_type = message.sender_chat.type if message.sender_chat else message.chat.type
    name = message.text

    if chat_type.name in ["CHANNEL"]:
        text = f"""
#DETECT_SENDER_AS_CHANNEL

**CHANNEL: {message.sender_chat.title} ({message.sender_chat.id})** 
`CHAT: {message.chat.title} ({message.chat.id})`
**MESSAGE: You Cannot Request Via Channel**"""
        chat_channel = await message.reply_text(text, quote=True)
        await asyncio.sleep(5)
        await chat_channel.delete()
        await message.delete()
        return

    if temp.TEMP_USER.get(message.from_user.id) == "edit":
        del temp.TEMP_USER[message.from_user.id]
    else:
        return

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            await check_manual_filter(client, group_id, keyword, message, 0)
            return
            # reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            #
            # if reply_text:
            #     reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")
            #
            # if btn is not None:
            #     try:
            #         if fileid == "None":
            #             if btn == "[]":
            #                 await message.reply_text(reply_text, disable_web_page_preview=True)
            #             else:
            #                 button = eval(btn)
            #                 await message.reply_text(
            #                     reply_text,
            #                     disable_web_page_preview=True,
            #                     reply_markup=InlineKeyboardMarkup(button)
            #                 )
            #         elif btn == "[]":
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or ""
            #             )
            #         else:
            #             button = eval(btn)
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or "",
            #                 reply_markup=InlineKeyboardMarkup(button)
            #             )
            #     except Exception as e:
            #         logger.exception(e)
            #     break


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    global SINGLE_BUTTON
    ident, req, key, offset = query.data.split("_")
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(req) not in [query.from_user.id, 0]:
        return await query.answer(
            "കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
            show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You Are Using One Of My Old Messages, Please Send The Request Again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    settings = await sett_db.get_settings(str(query.message.chat.id))
    if settings is not None:
        SINGLE_BUTTON = settings["button"]
        SPELL_CHECK_REPLY = settings["spell_check"]
        IMDB = settings["imdb"]

    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] - 🎬 {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )

    btn.insert(0, [
        InlineKeyboardButton("⭕️ Nᴇᴡ Uᴘᴅᴀᴛᴇs ⭕️", url="https://t.me/jns_movies")
    ])

    btn.insert(0, [
        InlineKeyboardButton("⭕️ ᴘᴍ ᴍᴇ ⭕️", url="https://t.me/jintons"),
        InlineKeyboardButton("⚜ ɴᴇᴡ ᴍᴏᴠɪᴇs ⚜", url="https://t.me/ott_new")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
                                  show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You Are Clicking On An Old Button Which Is Expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking For Movie In Database...')
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        k = await query.message.edit('This Movie Not Found In DataBase')
        await asyncio.sleep(10)
        await query.message.reply_to_message.delete()
        await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    first_name = query.from_user.first_name
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    help_match = re.match(r"help_", query.data)
    close_match = re.match(r"close_btn", query.data)

    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type.name == "PRIVATE":
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make Sure I'm Present In Your Group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm Not Connected To Any Groups!\nCheck /connections Or Connect To Any Groups",
                    quote=True
                )
                return

        elif chat_type.name in ["GROUP", "SUPERGROUP"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You Need To Be Group Owner Or An Auth User To Do That!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type.name == "PRIVATE":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type.name in ["GROUP", "SUPERGROUP"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Thats not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard
        )
        return
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**"
            )
        else:
            await query.message.edit_text('Some error occured!!')
        return
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!"
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!"
            )
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There Are No Active Connections!! Connect To Some Groups First.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        user = query.message.reply_to_message.from_user.id
        ad_user = query.from_user.id

        settings = await sett_db.get_settings(str(query.message.chat.id))
        if settings is not None:
            SINGLE_BUTTON = settings["button"]
            SPELL_CHECK_REPLY = settings["spell_check"]
            P_TTI_SHOW_OFF = settings["botpm"]
            IMDB = settings["imdb"]

        if FILE_PROTECT.get(query.from_user.id):
            del FILE_PROTECT[query.from_user.id]
        FILE_PROTECT[query.from_user.id] = str(query.message.chat.id)
        if int(ad_user) in ADMINS:
            pass
        elif int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(
                "കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
                show_alert=True)

        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        f_sub_caption = f"<code>💾 Size: {size}</code>\n\n🌟༺ ──•◈•─ ─•◈•──༻🌟\n<b>➧ പുതിയ സിനിമകൾ / വെബ്‌ സീരീസ് " \
                    f"വേണോ? എന്നാൽ പെട്ടെന്ന് ഗ്രൂപ്പിൽ ജോയിൻ ആയിക്കോ\n\n🔊 Gʀᴏᴜᴘ: " \
                    f"@UniversalFilmStudio \n🔊 Gʀᴏᴜᴘ: @UniversalFilmStudioo \n🔊 " \
                    f"Cʜᴀɴɴᴇʟ: <a href='https://t.me/+uuLR9YwyRjg0ODQ0'>Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs</a> \n\n🎗️ʝσιи 🎗️ ѕнαяє🎗️ ѕυρρσят🎗️ </b>"

        f_caption = f_caption + f"\n\n{f_sub_caption}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            elif P_TTI_SHOW_OFF:     # P_TTI_SHOW_OFF
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=settings["file_secure"] if settings["file_secure"] else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    '🎭 Nᴇᴡ Uᴘᴅᴀᴛᴇs', url="https://t.me/jns_bots"
                                ),
                                InlineKeyboardButton(
                                    '🎭 ᴍᴏᴠɪᴇs', url="https://t.me/jns_movies"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "⚜ Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs ⚜", url="https://t.me/ott_new"
                                )
                            ]
                        ]
                    )
                )
                await query.answer('Check My PM, I Have Sent Files In Your PM', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock Me Dude!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Over Smart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        # files_ = await get_file_details(file_id)

        settings = None
        if FILE_PROTECT.get(query.from_user.id):
            grpid = FILE_PROTECT.get(query.from_user.id)
            settings = await sett_db.get_settings(str(grpid))
            del FILE_PROTECT[query.from_user.id]
        # FILE_PROTECT[message.from_user.id] = str(message.chat.id)

        if not settings:
            FILE_SECURE = False
        else:
            FILE_SECURE = settings["file_secure"]
        files_ = await get_file_details(file_id)
        if not files_:
            sts = await query.message.reply("`⏳ Please Wait...`", parse_mode='markdown')
            msgs = BATCH_FILES.get(file_id)
            if not msgs:
                file = await client.download_media(file_id)
                try:
                    with open(file) as file_data:
                        msgs = json.loads(file_data.read())
                except:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
            await asyncio.sleep(1)
            await sts.delete()
            for msg in msgs:
                title = msg.get("title")
                size = get_size(int(msg.get("size", 0)))
                f_caption = msg.get("caption", "")
                file_type = msg.get("file_type")
                entities = msg.get("entities")

                if f_caption is None:
                    f_caption = f"{title}"
                f_sub_caption = f"<code>💾 Size: {size}</code>\n\n🌟༺ ──•◈•─ ─•◈•──༻🌟\n<b>➧ പുതിയ സിനിമകൾ / വെബ്‌ സീരീസ് " \
                                f"വേണോ? എന്നാൽ പെട്ടെന്ന് ഗ്രൂപ്പിൽ ജോയിൻ ആയിക്കോ\n\n🔊 Gʀᴏᴜᴘ: " \
                                f"@UniversalFilmStudio \n🔊 Gʀᴏᴜᴘ: @UniversalFilmStudioo \n🔊 " \
                                f"Cʜᴀɴɴᴇʟ: <a href='https://t.me/+uuLR9YwyRjg0ODQ0'>Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs</a> \n\n🎗️ʝσιи 🎗️ ѕнαяє🎗️ ѕυρρσят🎗️ </b>"

                # f_caption + f"\n\n<code>┈•••✿ @UniversalFilmStudio ✿•••┈\n\n💾 Size: {size}</code>"
                try:
                    await query.message.delete()
                    if file_type not in ["video", 'audio', 'document']:
                        await client.send_cached_media(
                            chat_id=query.from_user.id,
                            file_id=msg.get("file_id"),
                            caption=f_caption,
                            protect_content=FILE_SECURE,
                            caption_entities=entities,
                        )
                    else:
                        await client.send_cached_media(
                            chat_id=query.from_user.id,
                            file_id=msg.get("file_id"),
                            caption=f_caption + f"\n\n{f_sub_caption}",
                            protect_content=FILE_SECURE,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            '🎭 Nᴇᴡ Uᴘᴅᴀᴛᴇs', url="https://t.me/UFSFilmUpdate"
                                        ),
                                        InlineKeyboardButton(
                                            '🎭 ᴍᴏᴠɪᴇs', url="https://t.me/UniversalFilmStudio"
                                        )
                                    ],
                                    [
                                        InlineKeyboardButton(
                                            "⚜ Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs ⚜", url="https://t.me/+uuLR9YwyRjg0ODQ0"
                                        )
                                    ]
                                ]
                            )
                        )
                except Exception as err:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, f"{str(err)}")
                await asyncio.sleep(0.5)
            return await query.message.reply(f"<b><a href='https://t.me/UniversalFilmStudio'>Thank For Using Me...</a></b>")

        files_ = await get_file_details(file_id)
        if not files_:
            return await query.message.reply('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        f_sub_caption = f"<code>💾 Size: {size}</code>\n\n🌟༺ ──•◈•─ ─•◈•──༻🌟\n<b>➧ പുതിയ സിനിമകൾ / വെബ്‌ സീരീസ് " \
                        f"വേണോ? എന്നാൽ പെട്ടെന്ന് ഗ്രൂപ്പിൽ ജോയിൻ ആയിക്കോ\n\n🔊 Gʀᴏᴜᴘ: " \
                        f"@UniversalFilmStudio \n🔊 Gʀᴏᴜᴘ: @UniversalFilmStudioo \n🔊 " \
                        f"Cʜᴀɴɴᴇʟ: <a href='https://t.me/+uuLR9YwyRjg0ODQ0'>Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs</a> \n\n🎗️ʝσιи 🎗️ ѕнαяє🎗️ ѕυρρσят🎗️ </b>"

        f_caption = f_caption + f"\n\n{f_sub_caption}"
        try:
            await query.message.delete()
            await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=FILE_SECURE,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                '🎭 Nᴇᴡ Uᴘᴅᴀᴛᴇs', url="https://t.me/UFSFilmUpdate"
                            ),
                            InlineKeyboardButton(
                                '🎭 ᴍᴏᴠɪᴇs', url="https://t.me/UniversalFilmStudio"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "⚜ Nᴇᴡ Oᴛᴛ Mᴏᴠɪᴇs ⚜", url="https://t.me/+uuLR9YwyRjg0ODQ0"
                            )
                        ]
                    ]
                )
            )
        except Exception as e:
            return await query.message.reply(str(e))

    elif query.data == "pages":
        await query.answer()
        
        
    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/jns_bots')
            ],
            [
                InlineKeyboardButton('ℹ Help', callback_data='help'),
                InlineKeyboardButton('😊 About', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_JNS_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup
        )
    elif query.data == "jns123":
        buttons = [
            [
                InlineKeyboardButton('🏠 Home', callback_data='start'),
                InlineKeyboardButton('🔐 Close', callback_data='close_data')
            ]
        ]       
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT.format(message.from_user.mention if message.from_user else message.chat.title,
                                        temp.U_NAME,temp.B_NAME), 
            reply_markup=reply_markup
        )
        
    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton('📍Features📍', callback_data='jns123')
            ],
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/jns_bots')
            ],
            [
                InlineKeyboardButton('🏠 Home', callback_data='start'),
                InlineKeyboardButton('😊 About', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_JNS_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup
        )
                   # buttons = [
        #     [
        #         InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
        #         InlineKeyboardButton('Auto Filter', callback_data='autofilter')
        #     ],
        #     [
        #         InlineKeyboardButton('Connection', callback_data='coct'),
        #         InlineKeyboardButton('Extra Mods', callback_data='extra')
        #     ],
        #     [
        #         InlineKeyboardButton('🏠 Home', callback_data='start'),
        #         InlineKeyboardButton('🔮 Status', callback_data='stats')
        #     ]
        # ]
        # reply_markup = InlineKeyboardMarkup(buttons)
        # await query.message.edit_text(
        #     text=script.HELP_TXT.format(query.from_user.mention),
        #     reply_markup=reply_markup
        # )
        

        
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton('🏷JNS MOVIES🏷', url='https://t.me/JNS_MOVIES')
            ],
            [
                InlineKeyboardButton('❤️‍🔥ＪƝ⟆ ᗷ〇Ƭ⟆❤️‍🔥', url='https://t.me/JNS_BOTS')
            ],
            [
                InlineKeyboardButton('🏠 Home', callback_data='start'),
                InlineKeyboardButton('🔐 Close', callback_data='close_data')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_JNS_TXT.format(temp.B_NAME),
            reply_markup=reply_markup
        )
    elif query.data == "source":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "manuelfilter":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('⏹️ Buttons', callback_data='button')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "button":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='manuelfilter')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "autofilter":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "coct":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "extra":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('👮‍♂️ Admin', callback_data='admin')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "admin":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='extra')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup
        )
    elif query.data == "stats":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('♻️', callback_data='rfrsh')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup
        )
        await asyncio.sleep(5)
        await client.request_callback_answer(query.message.chat.id, query.message.id, "help")
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('♻️', callback_data='rfrsh')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup
        )
    elif query.data == "imdb":
        i, movie = query.data.split('#')
        imdb = await get_poster(query=movie, id=True)
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')}",
                    url=imdb['url'],
                )
            ]
        ]
        if imdb:
            caption = IMDB_TEMPLATE.format(
                query=imdb['title'],
                title=imdb['title'],
                votes=imdb['votes'],
                aka=imdb["aka"],
                seasons=imdb["seasons"],
                box_office=imdb['box_office'],
                localized_title=imdb['localized_title'],
                kind=imdb['kind'],
                imdb_id=imdb["imdb_id"],
                cast=imdb["cast"],
                runtime=imdb["runtime"],
                countries=imdb["countries"],
                certificates=imdb["certificates"],
                languages=imdb["languages"],
                director=imdb["director"],
                writer=imdb["writer"],
                producer=imdb["producer"],
                composer=imdb["composer"],
                cinematographer=imdb["cinematographer"],
                music_team=imdb["music_team"],
                distributors=imdb["distributors"],
                release_date=imdb['release_date'],
                year=imdb['year'],
                genres=imdb['genres'],
                poster=imdb['poster'],
                plot=imdb['plot'],
                rating=imdb['rating'],
                url=imdb['url'],
                **locals()
            )
        else:
            caption = "No Results"
        if imdb.get('poster'):
            try:
                await query.message.reply_photo(photo=imdb['poster'], caption=caption,
                                                reply_markup=InlineKeyboardMarkup(btn))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                await query.message.reply_photo(photo=imdb['poster'], caption=caption,
                                                reply_markup=InlineKeyboardMarkup(btn))
            except Exception as e:
                logger.exception(e)
                await query.message.reply(caption, reply_markup=InlineKeyboardMarkup(btn),
                                          disable_web_page_preview=False)
            await query.message.delete()
        else:
            await query.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
        await query.answer()
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id, time = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return

        if set_type == "delete":
            time = int(time) + 120
            await sett_db.update_settings(grp_id, set_type, True if (0 < int(time) <= 900) else False,
                                          time if (0 < int(time) <= 900) else 0)
        else:
            await sett_db.update_settings(grp_id, set_type, False if status == "True" else True, 0)

        settings = await sett_db.get_settings(str(grp_id))

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Aᴜᴛᴏ Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton(f'{settings["delete_time"]} Sᴇᴄ' if settings["auto_delete"] else '❌ Nᴏ',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["welcome"] else '❌ Nᴏ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)

    # ######################### MODULE HELP START #############################################################
    try:
        if mod_match:
            module = mod_match.group(1)
            text = "Here is the help for the **{}** module:\n".format(HELPABLE[module].__mod_name__) \
                   + HELPABLE[module].__help__
            await query.message.edit_text(text=text,
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        elif help_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))
        elif close_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        await client.answer_callback_query(query.id)
        # await query.message.delete()
        # bot.delete_message(update.effective_chat.id, update.effective_message.id - 1)
    except BadRequest as excp:
        if excp.message == "Message Is Not Modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message Can't Be Deleted":
            pass
        else:
            logging.exception("Exception In Help Buttons. %s", str(query.data))

    # ######################### MODULE HELP END #############################################################


async def check_manual_filter(client, group_id, keyword, message, msg):
    reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
    # if bool(msg.message.reply_to_message):
    #     message = msg.message.reply_to_message
    # else:
    #     message = msg

    if reply_text:
        reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

    settings = await sett_db.get_settings(str(group_id))
    if settings is not None:
        AUTO_DELETE = settings["auto_delete"]
        DELETE_TIME = settings["delete_time"]

    if AUTO_DELETE:
        reply_text = reply_text + f"<b><u>Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Dᴇʟᴇᴛᴇ Tʜɪs Rᴇϙᴜᴇsᴛ Aғᴛᴇʀ {TimeFormatter(int(DELETE_TIME) * 1000)}</u></b>"

    if btn is not None:
        try:
            if FILE_PROTECT.get(message.from_user.id):
                del FILE_PROTECT[message.from_user.id]
                # del FILE_PROTECT['631110062']
                del FILE_PROTECT['1636552877']
                del FILE_PROTECT['1535083157']
            # FILE_PROTECT['631110062'] = str(message.chat.id)
            FILE_PROTECT['1636552877'] = str(message.chat.id)
            FILE_PROTECT['1535083157'] = str(message.chat.id)

            if message.from_user.id not in ADMINS:
                FILE_PROTECT[message.from_user.id] = str(message.chat.id)

            if fileid == "None":
                if btn == "[]":
                    d_msg = await message.reply_text(reply_text, disable_web_page_preview=True)

                # if AUTO_DELETE:
                #     await asyncio.sleep(int(DELETE_TIME))
                #     await message.delete()
                #     await d_msg.delete()
                else:
                    button = eval(btn)
                    d_msg = await message.reply_text(
                        reply_text,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(button)
                    )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
            elif btn == "[]":
                d_msg = await message.reply_cached_media(
                    fileid,
                    caption=reply_text or ""
                )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
            else:
                button = eval(btn)
                d_msg = await message.reply_cached_media(
                    fileid,
                    caption=reply_text or "",
                    reply_markup=InlineKeyboardMarkup(button)
                )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
        except Exception as e:
            logger.exception(e)
