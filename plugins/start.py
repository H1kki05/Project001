import os
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, SECONDS
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user


# Start command with subscription check
@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except Exception as e:
            print(f"Error adding user: {e}")
    
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")

            # Handling message ID range extraction
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except Exception as e:
                    print(f"Error parsing message range: {e}")
                    return
                ids = range(start, end + 1) if start <= end else range(end, start + 1)
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except Exception as e:
                    print(f"Error parsing single message ID: {e}")
                    return
            
            temp_msg = await message.reply("Please wait...")
            try:
                messages = await get_messages(client, ids)
            except Exception as e:
                await message.reply_text("Something went wrong..!")
                print(f"Error getting messages: {e}")
                return
            await temp_msg.delete()

            dern = []
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
                else:
                    caption = "" if not msg.caption else msg.caption.html

                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                try:
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)
                    dern.append(snt_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    dern.append(snt_msg)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    pass

            k = await message.reply_text("Files will be deleted in 300 seconds to avoid copyright issues. Please forward the files.")
            await asyncio.sleep(SECONDS)

            for data in dern:
                try:
                    await data.delete()
                    await k.edit_text("Files deleted. Click the link again to get the file.")
                except Exception as e:
                    print(f"Error deleting message: {e}")
                    pass
        except Exception as e:
            print(f"Error processing start command: {e}")
            return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data="about"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )


# Handling users not joined
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    try:
        buttons = [
            [
                InlineKeyboardButton("Join Main 1", url=client.invitelink),
                InlineKeyboardButton("Join Main 2", url=client.invitelink2)
            ]
        ]
        try:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text='Try again',
                        url=f"https://t.me/{client.username}?start={message.command[1]}"
                    )
                ]
            )
        except IndexError:
            pass

        await message.reply(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in not_joined: {e}")


# Command to get the number of users
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    try:
        msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
        users = await full_userbase()
        await msg.edit(f"{len(users)} users are using this bot")
    except Exception as e:
        print(f"Error in get_users: {e}")


# Command to broadcast a message
@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        try:
            query = await full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0

            pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
            for chat_id in query:
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except UserIsBlocked:
                    await del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    print(f"Error broadcasting to {chat_id}: {e}")
                    unsuccessful += 1
                total += 1

            status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

            await pls_wait.edit(status)
        except Exception as e:
            print(f"Error in send_text: {e}")
    else:
        try:
            msg = await message.reply(REPLY_ERROR)
            await asyncio.sleep(8)
            await msg.delete()
        except Exception as e:
            print(f"Error sending reply error message: {e}")
