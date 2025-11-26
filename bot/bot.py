import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import settings
from handlers import creator, subscriber


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    # parse args after /start
    text = message.text or ""
    args = None
    if " " in text:
        args = text.split(" ", 1)[1].strip()

    # deep link: /start project_3
    if args and args.startswith("project_"):
        try:
            project_id = int(args.split("_", 1)[1])
        except ValueError:
            await message.answer("Invalid link parameter.")
            return

        telegram_id = message.from_user.id

        # 🔍 1. Check active subscription
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{settings.BACKEND_URL}/api/v1/subscriptions/active",
                    params={"telegram_id": telegram_id, "project_id": project_id},
                ) as resp_sub:
                    if resp_sub.status == 200:
                        sub = await resp_sub.json()
                        end_at = sub["end_at"]

                        await message.answer(
                            (
                                "🎉 You already have an active subscription to this channel.\n"
                                f"It is valid until: <b>{end_at}</b>\n\n"
                                "You can safely use the channel 😉"
                            ),
                            parse_mode="HTML",
                        )
                        return

                    elif resp_sub.status not in (200, 404):
                        text_err = await resp_sub.text()
                        print(
                            f"Error checking subscription: "
                            f"{resp_sub.status} {text_err}"
                        )

            except Exception as e:
                print("Exception while checking subscription:", e)

        # 💳 2. Load plans if there is no active subscription
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.BACKEND_URL}/api/v1/plans/project/{project_id}"
            ) as resp:
                if resp.status != 200:
                    await message.answer("Error while loading plans.")
                    return
                plans = await resp.json()

        if not plans:
            await message.answer("This channel has no active plans yet.")
            return

        # build keyboard with plans
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{plan['name']} — {plan['price']} {plan['currency']}",
                        callback_data=f"buy:{plan['id']}",
                    )
                ]
                for plan in plans
            ]
        )

        await message.answer(
            "Choose a plan to start your subscription:",
            reply_markup=keyboard,
        )
        return

    # default /start
    await message.answer(
        "Hi! I am Subscription Bot.\n"
        "Are you a channel creator or subscriber?\n"
        "/creator - I am creator\n"
        "/subscriber - I am subscriber"
    )


async def main():
    dp.include_router(creator.router)
    dp.include_router(subscriber.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
