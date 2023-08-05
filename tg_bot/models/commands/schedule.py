import asyncio

from tg_bot.services.schedule_parser import GroupScheduleParser

from ..schedule import Schedule
from ..db import db


async def select_schedule(group_name: str) -> list:
    schedule = await Schedule.query.where(Schedule.group_name == group_name).gino.first()
    return schedule

async def select_all_schedules() -> list[Schedule]:
    schedules = await Schedule.query.gino.all()
    return schedules

async def update_schedule(group_schedule_parser: GroupScheduleParser, schedule: Schedule):
    await group_schedule_parser.initialise_schedule_data()
    schedule_data = group_schedule_parser.get_schedule_data()
    await schedule.update(schedule_json=schedule_data).apply()

async def update_all_schedules():
    schedules: list[Schedule] = await select_all_schedules()
    schedule_update_tasks = []
    for schedule in schedules:
        group_schedule_parser = GroupScheduleParser(schedule.group_name)
        task = asyncio.create_task(update_schedule(group_schedule_parser, schedule))
        schedule_update_tasks.append(task)
        
    await asyncio.gather(*schedule_update_tasks, return_exceptions=True)

    
