import aiohttp
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters.command import CommandObject

from config import settings

router = Router()

# =========================================================
# 1) START with deep-link: /start connect_<code>
# =========================================================
@router.message(CommandStart(deep_link=True))
async def on_start_deeplink(message: Message, command: CommandObject):
    """
    User opens the bot via:
    https://t.me/<bot>?start=connect_<connection_code>

    We detect the code and show a simple, clean onboarding message.
    """

    payload = command.args  # aiogram 3 way
    if not payload or not payload.startswith("connect_"):
        # fallback: normal /start
        return await message.answer(
            "Welcome! 👋\n\n"
            "Use this bot to connect your private Telegram channel.\n"
            "Open the website to continue."
        )

    connection_code = payload.replace("connect_", "").strip()

    # Save code in FSM or in-memory dict? Simpler: store in user state.
    # But better: send the code back later manually on my_chat_member.

    # Store it temporarily inside aiogram user_data:
    message.bot['pending_code'] = message.bot.get('pending_code', {})
    message.bot['pending_code'][message.from_user.id] = connection_code

    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Add bot to your channel",
                url=f"https://t.me/{(await message.bot.get_me()).username}?startgroup=connect"
            )
        ]
    ]
)

    await message.answer(
        "🔗 Let's connect your private channel!\n\n"
        "Just two quick steps:\n"
        "1️⃣ Add this bot as **admin** to your private channel.\n"
        "2️⃣ That's it — I will detect it automatically.\n\n"
        "Choose your channel using the button below:",
        reply_markup=keyboard,
    )


# =========================================================
# 2) ON BOT ADDED AS ADMIN → HANDLE my_chat_member UPDATE
# =========================================================
@router.my_chat_member()
async def on_bot_added_to_channel(update: ChatMemberUpdated):
    """
    Telegram calls this whenever bot gets added/removed from chats.

    When bot is added to a channel, we:
    - extract user_id (who added us)
    - extract channel_id
    - extract channel title
    - send POST /projects/connect-channel to backend
    """

    chat = update.chat

    # Only care about channels
    if chat.type != "channel":
        return

    new_status = update.new_chat_member.status
    if new_status not in ("administrator", "member"):
        return

    user = update.from_user  # the person who added the bot

    bot = update.bot

    # Retrieve saved connection_code
    pending = bot.get("pending_code", {})
    connection_code = pending.get(user.id)

    if not connection_code:
        # No active connection session — ignore
        return

    # Prepare payload for backend
    payload = {
        "connection_code": connection_code,
        "telegram_channel_id": chat.id,
        "channel_title": chat.title,
    }

    # Call backend
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/projects/connect-channel",
            json=payload,
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                await bot.send_message(
                    user.id,
                    "❌ Failed to connect your channel.\n"
                    "Please try again.\n\n"
                    f"Technical error:\n{resp.status}\n{error}"
                )
                return

            await resp.json()  # We don't actually need the response

    # Remove the pending code (session is complete)
    pending.pop(user.id, None)

    # Send success message with button to go back to website
    dashboard_url = settings.FRONTEND_URL + "/app/channels"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", url=dashboard_url)]
        ]
    )

    await bot.send_message(
        user.id,
        f"✅ Your channel **{chat.title}** is now connected!\n\n"
        "You can now return to the dashboard and set up your subscription plans.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
