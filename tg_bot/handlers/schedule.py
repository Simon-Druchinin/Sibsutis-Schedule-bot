import locale, logging
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from tg_bot.services.schedule_parser import GroupScheduleParser
from tg_bot.keyboards.inline import get_date_choice_by_group, groups_choice
from tg_bot.keyboards.callback_data import schedule_date_callback, group_callback
from tg_bot.models.commands.schedule import select_schedule


async def handle_schedule_command(message: types.Message):
    group_name = message.get_args().upper()
    group_names = GroupScheduleParser.get_group_names()
    
    if not group_name:
        await message.answer("Выберете группу:", reply_markup=groups_choice)
        return
    elif group_name not in group_names:
        await message.answer("Группа не найдена :(\nВот список доступных групп:", reply_markup=groups_choice)
        return
    
    await show_schedule_calendar_message(message, group_name)
    
async def show_schedule_calendar_message(message: types.Message, group_name: str):
    locale.setlocale(locale.LC_TIME, '')
    current_month = datetime.now().strftime("%B")
    text = f'Расписание группы <b>{group_name}</b> на <u>{current_month}</u>'
    date_choice = get_date_choice_by_group(group_name)
    await message.answer(text, reply_markup=date_choice)

async def show_schedule_calendar_call(call: types.CallbackQuery, callback_data: dict):
    group_name = callback_data.get('name')
    locale.setlocale(locale.LC_TIME, '')
    current_month = datetime.now().strftime("%B")
    text = f'Расписание группы <b>{group_name}</b> на <u>{current_month}</u>'
    date_choice = get_date_choice_by_group(group_name)
    await call.message.answer(text, reply_markup=date_choice)

async def show_schedule_for_day(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    
    group_name = callback_data.get('group_name')
    group_schedule = GroupScheduleParser(group_name)
    schedule_data = await select_schedule(group_name)
    group_schedule.set_schedule_data(schedule_data.schedule_json)
    
    day = int(callback_data.get('schedule_day'))
    week_day = callback_data.get('week_day')
    date = callback_data.get('date')
    
    text = f"<b><u>{(week_day)} {date}</u></b>\n"
    text += group_schedule.get_schedule_for_day(day)
    await call.message.answer(text)
    
    
def register_schedule(dp: Dispatcher):
    dp.register_message_handler(handle_schedule_command, Command('schedule'))
    dp.register_callback_query_handler(show_schedule_calendar_call, group_callback.filter())
    dp.register_callback_query_handler(show_schedule_for_day, schedule_date_callback.filter())
