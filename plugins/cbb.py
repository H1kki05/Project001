

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>✑ Cʀᴇᴀᴛᴏʀ👨‍💻 :<a href='https://t.me/user?id={OWNER_ID}'>Tʜɪs Gᴜʏ</a>\n✑ Lᴀɴɢᴜᴀɢᴇ🗄 :<a>Pʏᴛʜᴏɴ</a>\n✑ Lɪʙʀᴀʀʏ🗃 : <a>Pʏʀᴏɢʀᴀᴍ</a>\n✑ Sᴏᴜʀᴄᴇ Cᴏᴅᴇ📄 : <a href='https://t.me/v15hnuf6n1x'>Gᴇᴛ Hᴇʀᴇ</a>\n✑ Dᴇᴠ🪛 : <a href='https://t.me/Mr_V_bots'>Mʀ.V Bᴏᴛs</a></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
