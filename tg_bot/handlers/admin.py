from aiogram import types, Dispatcher

from tg_bot.models.commands.schedule import update_all_schedules


async def force_update_schedule(message: types.Message):
    await message.answer('Запускаем обновление расписаний...')
    await update_all_schedules()
    await message.answer('Расписание всех групп было обновлено🛠')
    
def register_admin(dp: Dispatcher):
    dp.register_message_handler(force_update_schedule, commands=['force_update'], is_admin=True)
