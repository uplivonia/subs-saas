import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import settings

router = Router()


@router.message(Command("subscriber"))
async def subscriber_start(message: Message):
    await message.answer(
        "Subscriber mode.\n"
        "Когда вы перейдёте по специальной ссылке от автора, "
        "я покажу тарифы его канала."
    )


@router.callback_query(F.data.startswith("buy:"))
async def buy_plan(callback: CallbackQuery):
    plan_id = int(callback.data.split(":", 1)[1])
    await callback.answer()  # закрыть "часики" на кнопке

    # 1) Создаём подписку в backend
    payload = {
        "telegram_id": callback.from_user.id,
        "language": "en",
        "plan_id": plan_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/subscriptions/from-plan",
            json=payload,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                await callback.message.answer(
                    f"❌ Ошибка при создании подписки.\nСтатус: {resp.status}\n{text}"
                )
                return

            sub_data = await resp.json()

        project_id = sub_data.get("project_id")

        # 2) Тянем информацию о проекте (канале), чтобы узнать telegram_channel_id
        async with session.get(
            f"{settings.BACKEND_URL}/api/v1/projects/{project_id}"
        ) as resp2:
            if resp2.status != 200:
                await callback.message.answer(
                    "Подписка создана, но не удалось найти канал. Обратитесь к автору."
                )
                return
            project = await resp2.json()

    channel_id = project.get("telegram_channel_id")
    channel_title = project.get("title") or "канал"

    # 3) Создаём одноразовую инвайт-ссылку в канал
    try:
        invite_link = await callback.bot.create_chat_invite_link(
            chat_id=channel_id,
            member_limit=1,  # ссылка для одного пользователя
        )
        link = invite_link.invite_link
    except Exception as e:
        await callback.message.answer(
            "✅ Подписка создана, но я не смог выдать ссылку на канал.\n"
            "Скорее всего, бот не является администратором канала "
            "или у него нет прав приглашать пользователей.\n\n"
            f"Техническая ошибка: {e}"
        )
        return

    end_at = sub_data.get("end_at")

    await callback.message.answer(
        "✅ Подписка успешно создана.\n"
        f"Канал: {channel_title}\n"
        f"Подписка действует до: {end_at}\n\n"
        f"Вот твоя ссылка для входа в канал:\n{link}"
    )
