import datetime

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from .db import BaseModel

class Schedule(BaseModel):
    __tablename__ = 'schedules'

    id = Column(BigInteger(), primary_key=True)
    group_name = Column(String(255))
    schedule_json = Column(JSONB)
    updated_at = Column(
        DateTime(True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=func.now()
    )
