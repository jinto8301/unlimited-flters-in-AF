class script(object):
    START_JNS_TXT = """Hello {},
my name is <a href=https://t.me/{}>{}</a>
i'm simple manual filter bot with some Features 🤩

/settings to change autodelete time & Turn ON or OFF welcome message
""" 
    START_JNS1_TXT = """Hello {},
my name is <a href=https://t.me/{}>{}</a>
i'm simple manual filter bot with some Features 🤩
You can't use me in your groups without permission of my <a href=https://t.me/Jintons>Boss🔥</a>

/settings to change autodelete time & Turn ON or OFF welcome message
""" 
    HELP_JNS_TXT = """Checkout my featues""" 
    FTRE_JNS_TXT = """Checkout my featues""" 
    ABOUT_JNS_TXT = """✯ MY NAME: {}
    
✯ CREATOR: <a href=https://t.me/JNS_BOTS>❤️‍🔥ＪƝ⟆ ᗷ〇Ƭ⟆❤️‍🔥</a>

✯ LIBRABY: PYROGRAM

✯ LANGUAGE: PYTHON 3

✯ DATABASE: <a href=https://aws.amazon.com>AWS ⛓</a>

✯ BOT SERVER: <a href=https://aws.amazon.com>AWS 📡</a>
"""
    EXTRAMOD_TXT = """
/settings - Change autodelete time or OFF &  also turn ON or OFF welcome message ( group admin can only to it in PM)
/connect - Connect with group to manage group
/disconnect - To disconnect groups
/connections - To switch connected groups or To get list of connected groups
/filter | /add - Add manual filters
/del | /stop - To delete Manual filter
/delall - To delete all manual filters 
/filters | /viewfilters - check list of filters
/findsticker - to find sticker  from sticker ID
/stickerid - to find sticker ID from sticker
/getsticker - Change sticker package
/telegraph - Image to telegraph link (reply to image)
/speech - Text to voice (reply to text)
/tr - Translate text from one lang. to another    
/info - To get user info
/ban - ban users
/unban - unban users
/mute - mute users
/unmute - unmute users
/tmute - mute users for xx time
/tban - ban users for xx time
/leave - leave from working group (Admin only)
/chats - To get list of working group (Admin only)
/enable - Re-enable group (Admin only)
/disable - ban group (Admin only)
/broadcast - Send broadcast to users (Admin only)
/gpbroadcast | /gbbroadcast - to send broadcast to all working groups (Admin only)
"""    


    ADMINN_JNS_TXT = """
    <b>ADMIN COMMANDS</b>
/leave - leave from working group (Admin only)
/chats - To get list of working group (Admin only)
/enable - Re-enable group (Admin only)
/disable - ban group (Admin only)
/broadcast - Send broadcast to users (Admin only)    
/ban - ban users (Admin only)   
/unban - unban users (Admin only)   
/mute - mute users (Admin only) 
/unmute - unmute users (Admin only) 
/tmute - mute users for xx time (Admin only) 
/tban - ban users for xx time (Admin only) 
    """    
    FILTER_JNS_TXT = """
    <b>FILTER COMMANDS</b>
    <b>ADMIN ONLY</b>
/filter | /add - Add manual filters
/del | /stop - To delete Manual filter
/delall - To delete all manual filters
/filters | /viewfilters - check list of filters    
    
    """       
    CONNECTION_JNS_TXT = """
    <b>CONNECTION COMMANDS</b>
/settings - Change autodelete time or OFF &  also turn ON or OFF welcome message ( group admin can only to it in PM)
/connect - Connect with group to manage group
/disconnect - To disconnect groups
/connections - To switch connected groups or To get list of connected groups
    """      
    EXTRA_JNS_TXT = """
    <b>EXTRA COMMANDS</b>
/findsticker - to find sticker  from sticker ID
/stickerid - to find sticker ID from sticker
/getsticker - Change sticker package
/telegraph - Image to telegraph link (reply to image)
/speech - Text to voice (reply to text)
/tr - Translate text from one lang. to another    
/info - To get user info    
    """  
    
    
    
    
    
    
    START_TXT = """𝙷𝙴𝙻𝙾 {},
𝙼𝚈 𝙽𝙰𝙼𝙴 𝙸𝚂 <a href=https://t.me/{}>{}</a>, 𝙸 𝙲𝙰𝙽 𝙿𝚁𝙾𝚅𝙸𝙳𝙴 𝙼𝙾𝚅𝙸𝙴𝚂😍"""
    HELP_STRINGS = """
Hey Dear <b>{}</b>! My name is <b>UFS #V3.0</b>. I Am A Group Movie Bot, Here To Help You Get Around And Keep The Order In Your Groups!
I Have Lots Of Handy Features, 

<b>Helpful commands</b>:
- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
- /donate: Gives you info on how to support me and my creator.
{}

All commands can be used with the following: /
"""
    HELP_TXT = """𝙷𝙴𝚈 {}
𝙷𝙴𝚁𝙴 𝙸𝚂 𝚃𝙷𝙴 𝙷𝙴𝙻𝙿 𝙵𝙾𝚁 𝙼𝚈 𝙲𝙾𝙼𝙼𝙰𝙽𝙳𝚂."""

    SOURCE_TXT = """<b>NOTE:</b>


FSD

"""
    MANUELFILTER_TXT = """Help: <b>Filters</b>

- Filter is the feature were users can set automated replies for a particular keyword and UFS #V3.0 will respond whenever a keyword is found the message

<b>NOTE:</b>
1. UFS #V3.0 should have admin privilege.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

- UFS #V3.0 Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. UFS #V3.0 supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/UFSChatBot)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT1 = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of Eva Maria

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """Help: **Admin mods**

**NOTE:**
This module only works for my admins

**Commands and Usage:**
• /logs - `to get the recent errors`
• /stats - `to get status of files in db.`
• /delete - `to delete a specific file from db.`
• /users - `to get list of my users and ids.`
• /chats - `to get list of the my chats and ids `
• /leave  - `to leave from a chat.`
• /disable  -  `do disable a chat.`
• /ban  - `to ban a user.`
• /unban  - `to unban a user.`
• /channel - `to get list of total connected channels`
• /broadcast - `to broadcast a message to all users`"""
    STATUS_TXT = """<b>★ Tᴏᴛᴀʟ Fɪʟᴇs:</b> <code>{}</code>
<b>★ Tᴏᴛᴀʟ Usᴇʀs:</b> <code>{}</code>
<b>★ Tᴏᴛᴀʟ Cʜᴀᴛs:</b> <code>{}</code>
<b>★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>
<b>★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>"""
    
    
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
