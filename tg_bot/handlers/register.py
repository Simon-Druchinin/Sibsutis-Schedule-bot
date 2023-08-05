from aiogram import Dispatcher

from .echo import register_echo
from .admin import register_admin
from .base_commands import register_base_commands
from .schedule import register_schedule
from .subscribe import register_subscribe


def handlers_register(dp: Dispatcher):
    register_admin(dp)
    register_base_commands(dp)
    register_schedule(dp)
    register_subscribe(dp)
