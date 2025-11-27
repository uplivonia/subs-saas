import aiohttp
from aiogram import Router
from aiogram.types import (
    Message,
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import settings

router = Router()

# user_id -> connection_code
pending_codes: dict[int, str] = {}


async def start_connect_flow(message: Message, connection_code: str):
    """
    Called from /start connect_<code> in bot.py.

    - remembers connection_code for this user
    - registers/updates creator in backend
    - shows instructions + button to add bot to channel
    """

    # remember connection code for user
    pending_codes[message.from_user.id] = connection_code

    # register/update creator in backend
    payload = {
        "telegram_id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": message.from_user.username,
        "language": "en",
    }

    async with aiohttp.ClientSession() as session:
        try:
            await session.post(
                f"{settings.BACKEND_URL}/api/v1/users/",
                json=payload,
            )
        except Exception as e:
            print("Error while registering creator:", e)

    me = await message.bot.get_me()
    bot_username = me.username

    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Add bot to your channel",
                url=(
                    f"https://t.me/{bot_username}"
                    "?startchannel"
                    "&admin=post_messages+edit_messages+delete_messages+invite_users"
                ),
            )
        ]
    ]
)

    await message.answer(
        "🔗 Let's connect your private channel!\n\n"
        "1️⃣ Tap the button below and choose your private channel.\n"
        "2️⃣ Add this bot as an admin.\n"
        "3️⃣ I will automatically detect the channel and link it to your dashboard.",
        reply_markup=keyboard,
    )


@router.my_chat_member()
async def on_bot_added_to_channel(update: ChatMemberUpdated):
    """
    Telegram sends this update when the bot is added/removed from chats.

    When the bot is added as admin to a channel, we:
    - fetch the connection_code for the user who added the bot
    - send POST /projects/connect-channel to the backend
    - notify the user and show "Back to dashboard" button
    """
    chat = update.chat

    # only process channels
    if chat.type != "channel":
        return

    new_status = update.new_chat_member.status
    if new_status not in ("administrator", "member"):
        return

    user = update.from_user
    bot = update.bot

    # get previously stored connection_code for this user
    connection_code = pending_codes.get(user.id)
    if not connection_code:
        # no active connect session for this user
        return

    payload = {
        "connection_code": connection_code,
        "telegram_channel_id": chat.id,
        "channel_title": chat.title,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/projects/connect-channel",
            json=payload,
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                await bot.send_message(
                    user.id,
                    "❌ Failed to connect your channel.\n"
                    "Please try again.\n\n"
                    f"Technical error:\n{resp.status}\n{error_text}",
                )
                return

            data = await resp.json()
            project_id = data.get("project_id")
            print("Channel connected, project_id =", project_id)

    # connection completed -> remove code
    pending_codes.pop(user.id, None)

    dashboard_url = settings.FRONTEND_URL.rstrip("/") + "/app/channels"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to dashboard", url=dashboard_url)]
        ]
    )

    await bot.send_message(
        user.id,
        f"✅ Your channel <b>{chat.title}</b> is now connected!\n\n"
        "You can now go back to the dashboard and configure paid subscriptions.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
