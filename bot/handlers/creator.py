import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import settings

router = Router()


@router.message(Command("creator"))
async def creator_start(message: Message):
    # регистрируем/находим автора в backend (на всякий случай ещё раз)
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
        "👋 Привет! Твой аккаунт автора активен.\n\n"
        "Чтобы подключить канал:\n"
        "1️⃣ Добавь этого бота админом в свой канал.\n"
        "2️⃣ Перешли сюда любое сообщение из канала.\n\n"
        "Я сам сохраню канал в системе и пришлю ссылку для подписчиков 😉"
    )


@router.message(F.forward_from_chat)
async def connect_channel_from_forward(message: Message):
    """
    Автор пересылает сообщение из канала → создаём проект в backend.
    """
    # если переслано не из канала — игнорим
    if not message.forward_from_chat or message.forward_from_chat.type != "channel":
        return

    channel = message.forward_from_chat

    telegram_channel_id = channel.id
    title = channel.title
    username = channel.username  # может быть None

    # Создаём проект через backend
    payload = {
        "telegram_channel_id": telegram_channel_id,
        "title": title,
        "username": username,
        "active": True,
        "owner_telegram_id": message.from_user.id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/projects/",
            json=payload,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                await message.answer(
                    "❌ Не удалось сохранить канал.\n"
                    "Проверь, что ты автор/админ канала и попробуй позже.\n\n"
                    f"Техническая ошибка: {resp.status} {text}"
                )
                return

            project = await resp.json()

    # Получаем username бота, чтобы собрать ссылку
    me = await message.bot.get_me()
    bot_username = me.username

    project_id = project["id"]
    link = f"https://t.me/{bot_username}?start=project_{project_id}"

    await message.answer(
        "✅ Канал подключён!\n"
        f"Название: <b>{title}</b>\n"
        f"ID: <code>{telegram_channel_id}</code>\n\n"
        "Вот ссылка, которую можно давать подписчикам:\n"
        f"{link}",
        parse_mode="HTML",
    )
