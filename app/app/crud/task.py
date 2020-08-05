import copy
import json
from typing import List, Optional

from aiogram.types import User
from app.core.config import settings


def get_tasks() -> List[dict]:
    with open(settings.DATA_FOLDER / 'tasks.json') as file:
        return json.load(file)


class CRUDTask:
    tasks = {task['id']: task for task in get_tasks()}

    @staticmethod
    async def _handler(*args) -> List[dict]:
        args = copy.deepcopy(args)

        user = User.get_current()
        locale = user.locale

        if locale.language is None:
            return list(args)

        result = []
        for task in args:
            road_type: dict = task['road_type']
            task['road_type']: str = road_type.get(locale.language, road_type['en'])
            result.append(task)

        return result

    async def get_all(self) -> List[dict]:
        return await self._handler(*self.tasks.values())

    async def get(self, task_id: int) -> Optional[dict]:
        task: dict = self.tasks.get(task_id)

        if task is None:
            return None

        return (await self._handler(task))[0]

    async def exists(self, task_id: int) -> bool:
        task = await self.get(task_id)
        return task is not None

    async def count_tasks(self) -> int:
        return len(self.tasks)


crud_task = CRUDTask()
