import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

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
    # callback_data у нас вида "buy:1"
    plan_id = int(callback.data.split(":", 1)[1])
    # 1) Получаем информацию о тарифе из backend
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.BACKEND_URL}/api/v1/plans/{plan_id}") as resp:
            if resp.status != 200:
                text = await resp.text()
                await callback.message.answer(
                    f"❌ Не удалось получить тариф.\nСтатус: {resp.status}\n{text}"
                )
                return
            plan = await resp.json()

        amount = float(plan["price"])
        currency = plan["currency"]
        project_id = plan["project_id"]

        # 2) Создаём Stripe Checkout Session
        async with session.post(
            f"{settings.BACKEND_URL}/api/v1/payments/stripe/session",
            params={
                "plan_id": plan_id,
                "project_id": project_id,
                "amount": amount,
                "currency": currency,
                "telegram_id": callback.from_user.id,  # 👈 ДОБАВИЛИ ВАЖНОЕ ПОЛЕ
            },
        ) as resp2:
            if resp2.status != 200:
                text = await resp2.text()
                await callback.message.answer(
                    f"❌ Не удалось создать платёжную сессию.\nСтатус: {resp2.status}\n{text}"
                )
                return
            data = await resp2.json()

    checkout_url = data["checkout_url"]

    # 3) Отправляем пользователю кнопку с оплатой
    await callback.message.answer(
        "💳 Для оформления подписки оплатите тариф по ссылке:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Оплатить через Stripe 💸",
                        url=checkout_url,
                    )
                ]
            ]
        ),
    )

    # 👉 На этом этапе МЫ НЕ СОЗДАЁМ подписку и не выдаём инвайт!
    # Это сделаем позже через Stripe webhook (когда будет подтверждение оплаты).
