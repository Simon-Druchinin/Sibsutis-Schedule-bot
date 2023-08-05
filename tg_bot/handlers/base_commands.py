from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext


from tg_bot.models.commands.user import (get_subscription_data,
                                         email_exists, has_subscription,
                                         update_user_login, update_user_password)

async def start(message: types.Message, state: FSMContext):
    text = "Привет!👋\n"\
            "\n"\
            "🔍Тут ты сможешь найти:\n"\
            "1.) Расписание своей группы🕰\n"\
            "2.) Подписку для проставления посещений 📆\n"\
            "\n"\
            "Чтобы узнать подробнее, напиши - /help"
    await message.answer(text)
    await state.reset_state()
    
async def help(message: types.Message):
    text = "Доступные команды⚙️\n"\
            "• /help - справка по всем коммандам\n"\
            "• /subscribe - <b>оформить подписку</b>\n"\
            "• /schedule - расписание\n"\
            "• /schedule {group_name} - (Напр. /schedule ИП-112)\n"\
            "• /subscription_status - посмотреть статус и детали подписки\n"\
            "• /change_login {login} - изменить логин\n"\
            "• /change_password {passsword} - изменить пароль"    
    await message.answer(text)
    
async def subscription_status(message: types.Message):
    user_has_subscription = await has_subscription(message.chat.id)
    
    if not user_has_subscription:
        text = "У вас ещё не оформлена подписка🤷‍♂️"
        await message.answer(text)
        return
    
    subscription_data = await get_subscription_data(message.chat.id)
    is_subscription_active = subscription_data.get('is_subscription_active')
    subscription_end_date = subscription_data.get('subscription_end_date')
    login = subscription_data.get('login')
    password = subscription_data.get('password')
    status = 'Подписка активна✅' if is_subscription_active else 'Подписка закончилась❌'
    text = f"<u>Статус:</u> {status}\n"\
            f"📆Подписка действительна до <u>{subscription_end_date}</u>\n"\
            f"📬<u>Логин:</u> {login}\n"\
            f"🔓<u>Пароль:</u> {password}"

    await message.answer(text)

async def change_login(message: types.Message):
    login = message.get_args()
    
    if not await has_subscription(message.chat.id):
        await message.answer('У вас не оформлена подписка❗️')
        return
    if not login:
        await message.answer('Вы не предоставили логин❗️')
        return
    if await email_exists(login):
        await message.answer('Логин уже занят❗️')
        return
    await update_user_login(message.chat.id, login)
    await message.answer('<u>Логин</u> был успешно изменён✅')

async def change_password(message: types.Message):
    password = message.get_args()
    
    if not await has_subscription(message.chat.id):
        await message.answer('У вас не оформлена подписка❗️')
        return
    if not password:
        await message.answer('Вы не предоставили пароль❗️')
        return
    await update_user_password(message.chat.id, password)
    await message.answer('<u>Пароль</u> был успешно изменён✅')

def register_base_commands(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(subscription_status, commands=['subscription_status'])
    dp.register_message_handler(change_login, commands=['change_login'])
    dp.register_message_handler(change_password, commands=['change_password'])
