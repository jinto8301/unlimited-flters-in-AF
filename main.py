# (©)𝙐𝙁𝙎 𝘽𝙤𝙩𝙯

import re
import logging
import importlib

from database.restart_db import clean_restart_stage
from info import *
from bot import Bot
from Script import script
from plugins import ALL_MODULES
from pyrogram.errors import BadRequest
from plugins.misc import paginate_modules
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("plugins." + module_name)

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't Have Two Modules With The Same Name! Please Change One")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module


def main():
    Bot().run()


if __name__ == '__main__':
    logging.info("Successfully Loaded Modules: " + str(ALL_MODULES))
    main()

