from aiogram.dispatcher.filters.state import StatesGroup, State


class Subscription(StatesGroup):
    EnterLoginState = State()
    EnterPasswordState = State()
    ChoosePaymentTypeState = State()
    PrePaymentState = State()
    PaymentState = State()
    