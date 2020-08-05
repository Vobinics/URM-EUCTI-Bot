from typing import List, Optional

from app.models import User
from sqlalchemy import Column


class CRUDUser:
    need_fields = (User.place_residence, User.normal_distance, User.normal_speed)

    @staticmethod
    async def get(user_id: int) -> User:
        return await User.query.where(User.id == user_id).gino.first()

    @staticmethod
    async def create(user_id: int) -> User:
        return await User(id=user_id).create()

    @staticmethod
    async def update(user_obj: Optional[User] = None, **kwargs) -> User:
        return await user_obj.update(**kwargs).apply()

    async def get_or_create(self, user_id: int) -> User:
        return await self.get(user_id) or await self.create(user_id)

    async def is_registered(self, user_id: int) -> bool:
        user = await self.get_or_create(user_id)
        return None not in [getattr(user, column.key) for column in self.need_fields]

    async def next_need_column(self, user_id: int) -> Column:
        user = await self.get_or_create(user_id)
        for column in self.need_fields:
            if getattr(user, column.key) is None:
                return column

    async def get_done_tasks(self, user_id: int) -> List[int]:
        user = await self.get_or_create(user_id)
        done_tasks = list(user.done_tasks)
        done_tasks.sort()
        return done_tasks

    async def add_done_task(self, user_id: int, task_id: int) -> List[int]:
        user = await self.get_or_create(user_id)
        done_tasks = set(user.done_tasks)
        done_tasks.add(task_id)
        done_tasks = list(done_tasks)
        done_tasks.sort()
        await self.update(user, done_tasks=done_tasks)
        return done_tasks

    async def get_proceed_task(self, user_id: int) -> Optional[int]:
        user = await self.get_or_create(user_id)
        return user.proceed_task

    async def set_proceed_task(self, user_id: int, task_id: Optional[int] = None) -> int:
        user = await self.get_or_create(user_id)
        await self.update(user, proceed_task=task_id)
        return task_id

    async def unset_proceed_task(self, user_id: int) -> int:
        user = await self.get_or_create(user_id)
        last = user.proceed_task
        await self.update(user, proceed_task=None)
        return last


crud_user = CRUDUser()
