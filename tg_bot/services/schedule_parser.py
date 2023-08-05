import re
import json
from abc import ABC, abstractmethod
from datetime import datetime

import aiohttp
import asyncio

from bs4 import BeautifulSoup


class BaseScheduleParser(ABC):
    @abstractmethod
    async def _get_schedule_data(self) -> str:
        pass
    
    @abstractmethod
    async def _parse_schedule_data(self):
        pass
    
    @abstractmethod
    async def initialise_schedule_data(self):
        pass
    
    @abstractmethod
    def get_schedule_data(self) -> list[dict]:
        pass

class GroupScheduleParser(BaseScheduleParser):
    request_url = 'https://sibsutis.ru/students/schedule/?type=student&group=%(group_id)s'
    __schedule_data = []
    __group_ids = {
            'ИП-111': 3540993,
            'ИП-112': 3540994,
            'ИП-113': 3540995,
            'ИП-114': 3540997,
            'ИП-115': 3540996,
            'ИП-116': 3540998,
            'ИП-117': 3540999,
            'ИА-131': 3540989,
            'ИА-132': 3540990,
        }
    
    
    @staticmethod
    def get_groups_ids() -> dict[str, int]:
        return GroupScheduleParser.__group_ids
    
    @staticmethod
    def get_group_names() -> list[str]:
        return GroupScheduleParser.__group_ids.keys()
    
    def __init__(self, group_name: str):
        self.request_url = self.request_url % {'group_id': self.__group_ids[group_name]}
        
    async def _get_schedule_data(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.request_url) as response:                
                return await response.text()
    
    def _parse_schedule_data(self, schedule_data: str):
        soup = BeautifulSoup(schedule_data, 'lxml')
        layout_div = soup.find('div', attrs={'id': 'layout'})
        schedule = layout_div.find('script').text.strip()
        
        result = re.findall("{.*}", schedule)

        self.__schedule_data = [json.loads(data) for data in result]
    
    async def initialise_schedule_data(self):
        schedule_data = await self._get_schedule_data()
        self._parse_schedule_data(schedule_data)
    
    def get_schedule_data(self) -> list[dict]:
        return self.__schedule_data

    def set_schedule_data(self, schedule_data: list[dict]):
        self.__schedule_data = schedule_data
    
    def get_schedule_for_day(self, day: int) -> str:
        schedule_data = self.get_schedule_data()
        schedule_for_day = ""
        
        for index, lessons in enumerate(schedule_data[day]['ScheduleCell']):
            lesson = lessons.get('Lesson')

            begin_time = datetime.strptime(lessons['DateBegin'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            end_time = datetime.strptime(lessons['DateEnd'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            lesson_time = f'{begin_time} - {end_time}'

            if not lesson:
                schedule_for_day += f'{index+1}.) {lesson_time}\n'
                continue
            
            try:
                classroom = lesson['Classroom']['ClassroomName']
                classroom = f"(ауд. {classroom})"
            except KeyError:
                classroom = ''

            subject = lesson['Subject']
            lesson_type = lesson['LessonType']
            lesson_type = lesson_type[:3] if lesson_type.startswith('Лаб') else lesson_type[:4]
            

            schedule_for_day += f"{index+1}.) {lesson_time} {subject} ({lesson_type}.) {classroom}\n"
        
        return schedule_for_day
            
        
async def main():
    schedule_parser = GroupScheduleParser('ИП-112')
    await schedule_parser.initialise_schedule_data()
    
    print(len(str(schedule_parser.get_schedule_data())))
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    