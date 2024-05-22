import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, BadRequest
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, SECONDS
from helper_func import subscribed, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    try:
        id = message.from_user.id
        if not await present_user(id):
            await add_user(id)

        text = message.text
        if len(text) > 7:
            try:
                base64_string = text.split(" ", 1)[1]
                string = await decode(base64_string)
                argument = string.split("-")

                if len(argument) == 3:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end + 1)
                elif len(argument) == 2:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                else:
                    ids = []

                temp_msg = await message.reply("Processing...")
                messages = await get_messages(client, ids)

                await temp_msg.delete()

                delm = []
                for msg in messages:
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,
                                                    filename=msg.document.file_name) if bool(
                        CUSTOM_CAPTION) & bool(msg.document) else "" if not msg.caption else msg.caption.html

                    reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                    try:
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption,
                                                 parse_mode="html", reply_markup=reply_markup,
                                                 protect_content=PROTECT_CONTENT)
                        await asyncio.sleep(0.5)
                        delm.append(snt_msg)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption,
                                                 parse_mode="html", reply_markup=reply_markup,
                                                 protect_content=PROTECT_CONTENT)
                        delm.append(snt_msg)
                    except Exception as e:
                        print(f"Error copying message: {e}")

                k = await message.reply_text(
                    "Files will be deleted in 300 seconds to avoid copyright issues. Please forward the files.")

                await asyncio.sleep(SECONDS)

                for data in delm:
                    try:
                        await data.delete()
                        await k.edit_text("Files deleted. Click the link again to get the file.")
                    except Exception as e:
                        print(f"Error deleting message: {e}")

                return

            except IndexError:
                await message.reply("Invalid command usage.")
            except BadRequest as e:
                await message.reply(f"Bad request: {e}")
            except Exception as e:
                print(f"Error in start command: {e}")
                await message.reply_text("Something went wrong!")

        else:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("😊 About me", callback_data="about"),
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

    except Exception as e:
        print(f"Error in start command: {e}")
        await message.reply_text("Something went wrong!")


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
        print(f"Error in not_joined command: {e}")
        await message.reply_text("Something went wrong!")


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    try:
        msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
        users = await full_userbase()
        await msg.edit(f"{len(users)} users are using this bot.")

    except Exception as e:
        print(f"Error in get_users command: {e}")
        await message.reply_text("Something went wrong!")


@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    try:
        if message.reply_to_message:
            query = await full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0

            pls_wait = await message.reply("<i>Broadcasting message... This process will take some time</i>")
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
                except BadRequest as e:
                    print(f"Bad request error: {e}")
                    unsuccessful += 1
                except Exception as e:
                    print(f"Error broadcasting: {e}")
                    unsuccessful += 1

                total += 1

            status = f"""<b><u>Broadcast completed</u>

Total users      : <code>{total}</code>
Successful       : <code>{successful}</code>
Blocked accounts : <code>{blocked}</code>
Deleted accounts : <code>{deleted}</code>
Unsuccessful     : <code>{unsuccessful}</code></b>"""

            await pls_wait.edit(status)

        else:
            msg = await message.reply("Use this command as a reply to any Telegram message without any spaces.")
            await asyncio.sleep(8)
            await msg.delete()

    except Exception as e:
        print(f"Error in send_text command: {e}")
        await message.reply_text("Something went wrong!")