import asyncio
import datetime
import logging
from typing import List

import sqlalchemy as sa
from aiogram import Dispatcher
from gino import Gino

from tg_bot.config import load_config


db = Gino()
config = load_config(".env")


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=db.func.now(),
    )
    

async def db_on_startup(dispatcher: Dispatcher = None):
    logging.info("Setup PostgreSQL Connection")
    await db.set_bind(config.db.POSTGRES_URI)

async def db_on_shutdown(dispatcher: Dispatcher = None):
    bind = db.pop_bind()
    if bind:
        logging.info("Close PostgreSQL Connection")
        await bind.close()

async def create_all_db():
    await db.set_bind(config.db.POSTGRES_URI)
    await db.gino.create_all()
    await db.pop_bind().close()

async def recreate_all_db():
    await db.set_bind(config.db.POSTGRES_URI)
    await db.gino.drop_all()
    await db.gino.create_all()
    await db.pop_bind().close()
