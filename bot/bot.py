import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import settings
from handlers import creator, subscriber


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        # парсим аргументы после /start
        text = message.text or ""
        args = None
        if " " in text:
            # "/start project_1" -> "project_1"
            args = text.split(" ", 1)[1].strip()

        # если пришёл с deep-link вида ?start=project_1
        if args and args.startswith("project_"):
            try:
                project_id = int(args.split("_", 1)[1])
            except ValueError:
                await message.answer("Некорректный параметр ссылки.")
                return

            # тянем тарифы проекта с backend
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{settings.BACKEND_URL}/api/v1/plans/project/{project_id}"
                ) as resp:
                    if resp.status != 200:
                        await message.answer("Ошибка при загрузке тарифов.")
                        return
                    plans = await resp.json()

            if not plans:
                await message.answer("Для этого канала пока нет активных тарифов.")
                return

            # строим inline-кнопки по тарифам
            keyboard_rows = []
            for plan in plans:
                text_btn = f"{plan['name']} — {plan['price']} {plan['currency']}"
                keyboard_rows.append(
                    [
                        InlineKeyboardButton(
                            text=text_btn,
                            callback_data=f"buy:{plan['id']}",
                        )
                    ]
                )

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

            await message.answer(
                "Выберите тариф для оформления подписки:",
                reply_markup=keyboard,
            )
            return

        # обычный /start без параметров
        await message.answer(
            "Hi! I am Subscription Bot.\n"
            "Are you a channel creator or subscriber?\n"
            "/creator - I am creator\n"
            "/subscriber - I am subscriber"
        )

    dp.include_router(creator.router)
    dp.include_router(subscriber.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
