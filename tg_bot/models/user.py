from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger

from .db import TimedBaseModel

class User(TimedBaseModel):
    __tablename__ = 'users'

    id = Column(BigInteger(), primary_key=True)
    telegram_id = Column(Integer(), unique=True)
    login = Column(String(255), unique=True)
    password = Column(String(255))
    is_active = Column(Boolean(), default=True)
    subscription_end_date = Column(DateTime(True))
    notify_on_check_in = Column(Boolean(), default=True)
    payment_date = Column(DateTime(True))
    