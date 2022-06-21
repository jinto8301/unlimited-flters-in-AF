import logging
import asyncio
import logging.config

import pyromod.listen
from pyrogram import Client, __version__, enums
from pyrogram.raw.all import layer

import bot
from database.ia_filterdb import Media
from database.restart_db import clean_restart_stage
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, dispatcher, LOG_CHANNEL
from utils import temp

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)


class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        self.set_parse_mode(enums.ParseMode.DEFAULT)
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        dispatcher = self.dispatcher
        logging.info(LOG_STR)
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(f"{me.first_name} Has Started Running...🏃💨💨")

        restart_data = await clean_restart_stage()

        try:
            # print("[INFO]: SENDING ONLINE STATUS")
            if restart_data:
                logging.info(f"[INFO]: RESTARTING PROCESS")
                await bot.Bot.edit_message_text(self,
                    restart_data["chat_id"],
                    restart_data["message_id"],
                    "**Restarted Successfully**",
                )
                await bot.Bot.send_message(self, LOG_CHANNEL, "**Bot Updated Successfully**!")

            else:
                await bot.Bot.send_message(self, LOG_CHANNEL, "**Bot Restarted Successfully**!")
        except Exception as e:
            logging.info(f"[ERROR]: {str(e)}")
            pass

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")


