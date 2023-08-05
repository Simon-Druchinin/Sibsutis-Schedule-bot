import pytz
from datetime import datetime, timedelta

from asyncpg import UniqueViolationError

from tg_bot.models.user import User

from ..db import db

async def add_user(telegram_id: int, login: str, password: str):
    try:
        user = User(
            telegram_id=telegram_id,
            login=login,
            password=password
        )
        
        await user.create()
        
        return user
    except UniqueViolationError:
        return None

async def select_all_users() -> list[User]:
    users = await User.query.gino.all()
    return users

async def count_users() -> int:
    count = await db.func.count(User.id).gino.scalar()
    return count

async def select_user(telegram_id: int) -> User:
    user = await User.query.where(User.telegram_id == telegram_id).gino.first()
    return user

async def update_user_login(telegram_id: int, login: str):
    user: User = await select_user(telegram_id)
    await user.update(login=login).apply()
    
async def update_user_password(telegram_id: int, password: str):
    user: User = await select_user(telegram_id)
    await user.update(password=password).apply()

async def update_user_subscription_end_date(telegram_id: int):
    user: User = await select_user(telegram_id)
    is_subscription_active = await has_active_subscription(telegram_id)
    subscription_end_date = user.subscription_end_date if is_subscription_active else datetime.now()
    subscription_end_date += timedelta(days=30)
    await user.update(subscription_end_date=subscription_end_date, payment_date=datetime.now()).apply()

async def get_subscription_data(telegram_id: int) -> dict:
    user: User = await select_user(telegram_id)
    subscription_end_date = user.subscription_end_date
    is_subscription_active = await has_active_subscription(telegram_id)
    
    subscription_data = {
        'login': user.login,
        'password': user.password,
        'subscription_end_date': datetime.strftime(subscription_end_date, '%d.%m.%y'),
        'is_subscription_active': is_subscription_active
    }
    
    return subscription_data

async def email_exists(email: str) -> bool:
    email_exists = await db.scalar(db.exists().where(User.login == email).select())
    
    return email_exists

async def user_exists(telegram_id: int) -> bool:
    user_exists = await db.scalar(db.exists().where(User.telegram_id == telegram_id).select())
    
    return user_exists

async def has_active_subscription(telegram_id: int) -> bool:
    if not await has_subscription(telegram_id):
        return False
    
    user: User = await select_user(telegram_id)
    utc = pytz.UTC
    subscription_end_date = user.subscription_end_date.replace(tzinfo=utc)
    now = datetime.now().replace(tzinfo=utc)
    
    return subscription_end_date > now

async def has_subscription(telegram_id: int) -> bool:
    user: User = await select_user(telegram_id)
    
    return user and user.subscription_end_date is not None

async def select_users_with_active_subscriptions() -> list[User]:
    users = await select_all_users()
    users_with_active_subscriptions = [user for user in users if await has_active_subscription(user.telegram_id)]
    
    return users_with_active_subscriptions
    
