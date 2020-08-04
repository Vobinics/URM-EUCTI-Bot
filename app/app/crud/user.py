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

    async def update(self, user_id: int, **kwargs) -> User:
        user = await self.get_or_create(user_id)
        return await user.update(**kwargs).apply()

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


crud_user = CRUDUser()
