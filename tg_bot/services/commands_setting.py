from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand('schedule', 'Расписание'),
            BotCommand('subscribe', 'Оформить подписку'),
            BotCommand('subscription_status', 'Посмотреть статус и детали подписки'),
            BotCommand('help', 'Получить справку по всем коммандам')
        ]
    )
