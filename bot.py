import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tg_bot.config import load_config
from tg_bot.middlewares.db import DBMiddleware
from tg_bot.filters.admin import AdminFilter
from tg_bot.handlers.register import handlers_register
from tg_bot.services.commands_setting import set_default_commands

from tg_bot.models.db import db_on_startup, db_on_shutdown, create_all_db

from tg_bot.models.commands.schedule import update_all_schedules


logger = logging.getLogger(__name__)


def register_all_middlewares(dp: Dispatcher):
    dp.setup_middleware(DBMiddleware())

def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)

def register_all_handlers(dp: Dispatcher):
    handlers_register(dp)
    
async def set_all_default_commands(bot: Bot):
    await set_default_commands(bot)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-6s [%(asctime)s] - %(name)s - %(message)s'
    )
    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config
    
    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)
    
    await set_all_default_commands(bot)
    
    try:
        await db_on_startup(dp)
        await dp.start_polling()
        
    finally:
        await db_on_shutdown(dp)
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

