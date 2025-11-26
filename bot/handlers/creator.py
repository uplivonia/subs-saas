import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import settings

router = Router()


@router.message(Command("creator"))
async def creator_start(message: Message):
    """
    Creator onboarding (register creator in backend).
    """

    # Register / update creator in backend
    payload = {
        "telegram_id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": message.from_user.username,
        "language": "en",
    }

    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{settings.BACKEND_URL}/api/v1/users/",
            json=payload,
        )

    await message.answer(
        "👋 Welcome, creator!\n\n"
        "To connect your private Telegram channel:\n"
        "1️⃣ Add this bot as an **admin** to your channel.\n"
        "2️⃣ Forward **any message** from that channel to this chat.\n\n"
        "I will automatically detect the channel, save it in your dashboard, "
        "and generate a subscription link for your followers 😉"
    )


@router.message(F.forward_from_chat)
async def connect_channel_from_forward(message: Message):
    """
    Creator forwards a message from a channel → we register the channel as a Project.
    """

    # Only allow forwarded messages from channels
    if not message.forward_from_chat or message.forward_from_chat.type != "channel":
        return

    channel = message.forward_from_chat

    telegram_channel_id = channel.id
    title = channel.title
    username = channel.username  # may be None for private channels

    payload = {
        "telegram_channel_id": telegram_channel_id,
        "title": title,
        "username": username,
        "active": True,
        "owner_telegram_id": message.from_user.id,
    }

    # Create project in backend
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/projects/",
            json=payload,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                await message.answer(
                    "❌ Failed to save this channel.\n"
                    "Please make sure you are the channel owner/admin and try again.\n\n"
                    f"Technical error: {resp.status} {text}"
                )
                return

            project = await resp.json()

    # Bot username for subscription link
    me = await message.bot.get_me()
    bot_username = me.username

    project_id = project["id"]
    link = f"https://t.me/{bot_username}?start=project_{project_id}"

    await message.answer(
        "✅ Channel successfully connected!\n\n"
        f"• Title: <b>{title}</b>\n"
        f"• ID: <code>{telegram_channel_id}</code>\n\n"
        "Here is the personal subscription link you can share:\n"
        f"{link}",
        parse_mode="HTML",
    )
