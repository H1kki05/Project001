import os
import logging
from logging.handlers import RotatingFileHandler



#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7077211812:AAHKKvettcople6i__FaQ-9vldeHP2QdSJA")

#USER id of the bot(for getting files)
#BUSER_ID = os.environ.get("BUSER_ID")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "21165589"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "8cc762f4873e84a7cf0cbfd66a07244b")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1001971345822"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "2048030675"))

#Port
PORT = os.environ.get("PORT", "8080")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://file:link@cluster0.jth5g3y.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DATABASE_NAME", "a1pher_files")

#autodelete seconds
SECONDS = int(os.getenv("SECONDS", "340"))

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1001794747387"))
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2","-1002069266057"))
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
START_MSG = os.environ.get("START_MESSAGE", "ʜᴇʟʟᴏ🖐 {first}\n\nI ᴄᴀɴ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ғʀᴏᴍ <a href='https://t.me/A1pher'>Tᗴᗩᗰ ᗩ1ᑭᕼᗴᖇ</a> ᴛᴏ ᴍʏ ғᴀᴍɪʟʏ ᴀɴᴅ ᴛʜᴇʏ ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ᴡɪᴛʜ ᴍʏ ʟɪɴᴋs.")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ🖐 {first}\n\n<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ Jᴏɪɴ ɪɴ ᴍʏ Cʜᴀɴɴᴇʟ's ᴛᴏ ᴜsᴇ ᴍᴇ\n\nKɪɴᴅʟʏ Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ Cʜᴀɴɴᴇʟ</b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION",None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
if os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'False':
    DISABLE_CHANNEL_BUTTON = True
else:
    DISABLE_CHANNEL_BUTTON = False

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "Mʏ ᴀʙɪʟɪᴛʏ ɪs ᴛᴏ sᴇɴᴅ ғɪʟᴇs ᴏɴʟʏ"

ADMINS.append(OWNER_ID)
ADMINS.append(2048030675)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
