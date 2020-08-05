import copy
import json
from typing import List, Optional

from aiogram.types import User
from app.core.config import settings


def get_tasks() -> List[dict]:
    with open(settings.DATA_FOLDER / 'tasks.json') as file:
        return json.load(file)


def localed(table: dict):
    user = User.get_current()
    return table.get(user.locale.language, table['en'])


class CRUDTask:
    tasks = {task['id']: task for task in get_tasks()}

    @staticmethod
    async def _handler(*args) -> List[dict]:
        args = copy.deepcopy(args)

        if User.get_current().locale is None:
            return list(args)

        result = [
            {key: localed(var) if isinstance(var, dict) else var for key, var in task.items()}
            for task in args
        ]

        return result

    async def get_all(self) -> List[dict]:
        return await self._handler(*self.tasks.values())

    async def get(self, task_id: int) -> Optional[dict]:
        task: dict = self.tasks.get(task_id)

        if task is None:
            return None

        return (await self._handler(task))[0]

    async def get_by_title(self, task_title: str) -> Optional[dict]:
        for task in self.tasks.values():
            if task_title == localed(task['title']):
                return (await self._handler(task))[0]

    async def exists(self, task_id: int) -> bool:
        task = await self.get(task_id)
        return task is not None

    async def count_tasks(self) -> int:
        return len(self.tasks)


crud_task = CRUDTask()
