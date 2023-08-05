import calendar
from datetime import datetime, date

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.services.schedule_parser import GroupScheduleParser
from .callback_data import schedule_date_callback, group_callback, subcribe_callback


def get_current_month_keyboard(group_name: str) -> list[list[InlineKeyboardButton]]:
    now = datetime.now()
    month_format = now.strftime("%m")
    day_start, days_amount = calendar.monthrange(now.year, now.month)
    week_days = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
    current_week_of_the_year = date(now.year, now.month, 1).isocalendar().week
    
    days_per_row_count = day_start
    
    EMPTY_CALLBACK_VALUE = "_EMPTY_CALLBACK_VALUE"
    
    inline_keyboard = [[] for i in range(7)]
    inline_keyboard[0] = [InlineKeyboardButton(text=f'{day_of_week}', callback_data=EMPTY_CALLBACK_VALUE) for day_of_week in week_days]
    inline_keyboard[1] = [InlineKeyboardButton(text=" ", callback_data=EMPTY_CALLBACK_VALUE) for i in range(days_per_row_count)]
    inline_keyboard_row = 1
    callback_data = 0 if current_week_of_the_year % 2 == 1 else 7
    callback_data += day_start
    
    for day in range(days_amount):
        if days_per_row_count == 7:
            inline_keyboard_row += 1
            days_per_row_count = 0
            
        if callback_data == 14:
            callback_data = 0
            
        day_format = datetime(now.year, now.month, day+1).strftime("%d")
        
        text = f"{day_format}"
        if day+1 == now.day:
            text = "⭐️" + text
            
        inline_keyboard[inline_keyboard_row].append(
            InlineKeyboardButton(
                text=text,
                callback_data=schedule_date_callback.new(
                    date=f"{day_format}.{month_format}",
                    schedule_day=callback_data,
                    group_name=group_name,
                    week_day=week_days[callback_data - 7 if callback_data > 6 else callback_data]
                )
            )
        )
        
        days_per_row_count += 1
        callback_data += 1
    
    while days_per_row_count != 7:
        inline_keyboard[inline_keyboard_row].append(InlineKeyboardButton(text=" ", callback_data=EMPTY_CALLBACK_VALUE))
        
        days_per_row_count += 1
    
    return inline_keyboard


def get_date_choice_by_group(group_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=7,
                                   inline_keyboard=get_current_month_keyboard(group_name)
                                   )

groups_choice = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(
                                                text=group_name, callback_data=group_callback.new(
                                                    name=group_name
                                                )
                                            )
                                        ] for group_name in GroupScheduleParser.get_group_names()
                                    ] 
)

start_subscribe_keyboard = InlineKeyboardMarkup(row_width=1)
start_subscribe_keyboard.add(
     InlineKeyboardButton(
        text="Перейти к оформлению подписки🚀",
        callback_data=subcribe_callback.new(command_type="start_subscription")                                                                                   
    )
)
                                           
def get_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    payment_keyboard = InlineKeyboardMarkup(row_width=1)
    payment_keyboard.add(
        InlineKeyboardButton(
            text="Перейти к оплате 💳",
            url=payment_url,
            callback_data=subcribe_callback.new(command_type="pay")
        )
    )
    payment_keyboard.add(
        InlineKeyboardButton(
            text="Отмена",
            callback_data=subcribe_callback.new(command_type="cancel")
        )
    )
    
    return payment_keyboard

choose_payment_type_keyboard = InlineKeyboardMarkup(row_width=1)
choose_payment_type_keyboard.add(
        InlineKeyboardButton(
            text="🌿Оплатить подписку (поддержать авторов)🌿",
            callback_data=subcribe_callback.new(command_type="pay_for_subscription")
        )
    )
choose_payment_type_keyboard.add(
        InlineKeyboardButton(
            text="Получить подписку бесплатно🆓",
            callback_data=subcribe_callback.new(command_type="get_free_subscribtion")
        )
    )
choose_payment_type_keyboard.add(
        InlineKeyboardButton(
            text="Отмена",
            callback_data=subcribe_callback.new(command_type="cancel")
        )
    )
