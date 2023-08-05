import asyncio
from uuid import uuid4
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from tg_bot.services.async_yoomoney import Quickpay, Client
from tg_bot.keyboards.inline import get_payment_keyboard, start_subscribe_keyboard, choose_payment_type_keyboard
from tg_bot.keyboards.callback_data import subcribe_callback
from tg_bot.states.subscription import Subscription
from tg_bot.models.commands.user import (email_exists, user_exists,
                                         select_user, add_user, update_user_subscription_end_date)


async def subscribe_faq(message: types.Message):
    text = "Вы хотите оформить подписку для автоматических отметок о посещении в системе ЭИОС СибГУТИ.\n"\
            "\n<b>FAQ:</b>\n"\
            "1.) <u>Почему подписка платная?</u>\n"\
            "   Бот и скрипт, который проставляет посещения, работают на хостинге в автоматическом режиме.🖥\n"\
            "Хостинг - вещь платная, отсюда и платная подписка.💸\n"\
            "К счастью, сумма совсем небольшая - <b>всего 50 рублей</b>😁\n"\
            "\n 2.) <u>Потребуется ли мои логин и пароль от ЭИОСа?</u>\n"\
            "   Да, для того, чтобы вас отметить, надо зайти под вашими учётными данными⌨️\n"\
            "Однако можете не переживать за их сохранность:\n"\
            "Доступ к данным есть только у администратора.🔐\n"\
            "\n3.) <u>Как узнать срок действия подписки?</u>\n"\
            "   🟢 /subscription_status\n"\
            "\n4.) <u>Как изменить логин или пароль?</u>\n"\
            "   🟢 /change_login {login}\n"\
            "   🟢 /change_password {password}\n"\
            "\n5.) <u>Что делать, если меня не отметили в ЭИОСЕ?</u>\n"\
            "   Верятно, вы неправльно ввели логин или пароль🛑\n"\
            "Поменяйте их при помощи соответствующих комманд💬\n"\
            "Или свяжитесь с администратором @simon_druchinin👩‍🚀\n"
                
    
    await message.answer(text, reply_markup=start_subscribe_keyboard)
    
async def cancel_subscription(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Вы отменили оформление подписки🙅‍♂️", show_alert=True)
    await call.message.edit_reply_markup()
    await state.reset_state()

async def get_user_login(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if await user_exists(call.message.chat.id):
        text = "<b><u>Продление подписки</u></b>🛂\n"\
                "Если хотите предоставить другие учётные данные,\n"\
                "То используйте комманды:\n"\
                "/change_login {login}\n"\
                "/change_password {password}"
        message = await call.message.answer(text)
        await Subscription.PrePaymentState.set()
        await prepayment_user_credentials_check(message, state)
        return
    
    await call.message.answer("Введите ваш <u>логин</u> от ЭИОС📬")
    await Subscription.EnterPasswordState.set()

async def retype_user_login(message: types.Message, state: FSMContext):
    await message.answer("Данный логин уже занят❌\nВведите ваш <u>логин</u> от ЭИОС📬")
    await Subscription.EnterPasswordState.set()

async def get_user_password(message: types.Message, state: FSMContext):
    login = message.text
    
    if await email_exists(login):
        await Subscription.EnterLoginState.set()
        await retype_user_login(message, state)
        return
        
    await state.update_data(login=login)
    await message.answer("Введите ваш <u>пароль</u> от ЭИОС🔓")
    await Subscription.ChoosePaymentTypeState.set()

async def choose_payment_type(message: types.Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    text = "Выберете тип оплаты 🏦"
    await message.answer(text, reply_markup=choose_payment_type_keyboard)

async def handle_prepayment_state(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await Subscription.PrePaymentState.set()
    await prepayment_user_credentials_check(call.message, state)

async def get_free_subscribtion(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    if not await user_exists(call.message.chat.id):
        login = data.get('login')
        password = data.get('password')
        user = await add_user(call.message.chat.id, login, password)
        if not user:
            await call.message.answer("Ошибка при создании пользователя❌\n Попроюуйте ещё раз🛠")
            return
   
    await update_user_subscription_end_date(call.message.chat.id)
    
    await call.message.answer(f"<u>Подписка</u> получена✅")
    await state.reset_state()

async def prepayment_user_credentials_check(message: types.Message, state: FSMContext):
    await message.answer('Спасибо, что поддерживаете авторов ❤️')
    if await user_exists(message.chat.id):
        user = await select_user(message.chat.id)
        login = user.login
        password = user.password
    else:
        data = await state.get_data()
        login = data.get('login')
        password = data.get('password')
        
    payment_uuid = f'payment:{message.chat.id}:{uuid4().hex}'
    await state.update_data(login=login)   
    await state.update_data(password=password)
    await state.update_data(payment_uuid=payment_uuid)
    
    quickpay = Quickpay(
        receiver="4100118127309241",
        quickpay_form="shop",
        targets="Оплата подписки для автоматического проставления посещений в среде ЭИОС СибГУТИ.",
        formcomment="Оплата подписки для автоматического проставления посещений в среде ЭИОС СибГУТИ.",
        comment="Оплата подписки для автоматического проставления посещений в среде ЭИОС СибГУТИ.",
        message=payment_uuid,
        paymentType="SB",
        sum=2,
        label=payment_uuid
    )
    redirect_url = await quickpay.get_redirect_url()
    if not redirect_url:
        text = "Сервисы Yoomoney <b>не отвечают</b>💭\nПопробуйте повторить попытку позднее🕑"
        message = await message.answer(text)
        return
    payment_keyboard = get_payment_keyboard(redirect_url)
    text =  f"📬Ваш Логин: <b>{login}</b>\n🔓Пароль:<b>{password}</b>\n"\
            "❗️Ссылка на оплату действительна <u>15 минут</u>❗️"
            
    message = await message.answer(text, reply_markup=payment_keyboard)
    await Subscription.PaymentState.set()
    await payment_check(message, state)

async def payment_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_uuid = data.get('payment_uuid')
    PAYMENT_TOKEN = message.bot['config'].misc.PAYMENT_TOKEN
    client = Client(PAYMENT_TOKEN)
    success = True
    start_payment_time = datetime.now()
    while True:
        current_state = await state.get_state()
        seconds_passed_since_start = (datetime.now() - start_payment_time).seconds
        if (current_state != "Subscription:PaymentState") or (seconds_passed_since_start > 900):
            try:
                await message.edit_reply_markup()
            except MessageNotModified:
                pass
            if seconds_passed_since_start > 900:
                await state.reset_state()
            return
        
        history_operations = await client.operation_history(label=payment_uuid)
        operation = history_operations[-1] if len(history_operations) else None

        if operation and operation.status == 'success':
            success = True
            await message.edit_reply_markup()
            break
        elif operation:
            await message.edit_reply_markup()
            break
        
        await asyncio.sleep(10)
        
    error_text = "❌<b>Произошла ошибка</b>❌\nЕсли у вас списались средства:\nОбратитесь к администратору бота @simon_druchinin"
    if not success:
        await message.answer(error_text)
        return
    if not await user_exists(message.chat.id):
        login = data.get('login')
        password = data.get('password')
        user = await add_user(message.chat.id, login, password)
        if not user:
            await message.answer(error_text)
            return
   
    await update_user_subscription_end_date(message.chat.id)
    
    await message.answer(f"<u>Подписка</u> оплачена✅")
    await state.reset_state()

def register_subscribe(dp: Dispatcher):
    dp.register_message_handler(subscribe_faq, commands=['subscribe'])
    dp.register_callback_query_handler(get_user_login, subcribe_callback.filter(command_type="start_subscription"))
    dp.register_callback_query_handler(cancel_subscription, subcribe_callback.filter(command_type="cancel"), state='*')
    dp.register_message_handler(get_user_password, state=Subscription.EnterPasswordState)
    dp.register_message_handler(choose_payment_type, state=Subscription.ChoosePaymentTypeState)
    dp.register_callback_query_handler(handle_prepayment_state, subcribe_callback.filter(command_type="pay_for_subscription"), state=Subscription.ChoosePaymentTypeState)
    dp.register_message_handler(prepayment_user_credentials_check, state=Subscription.PrePaymentState)
    dp.register_callback_query_handler(get_free_subscribtion, subcribe_callback.filter(command_type="get_free_subscribtion"), state=Subscription.ChoosePaymentTypeState)
    