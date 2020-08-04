from aiogram import filters, types
from app.core.bot import dp
from app.core.language import _  # noqa
from app.crud import crud_user
from app.models import User
from app.utils import not_registered, check_value


@dp.message_handler(filters.CommandStart())
async def start(message: types.Message):
    # Welcome
    text = _("Hello! With this bot, you can subscribe to the EUC Testing Initiative for UniRoadMap to help us create "
             "a really polished and good product! Your data will be used to create unique settings for each EUC model "
             "for our navigation engine. Every personal information about you is stored securely and no one except "
             "our developers can access it.")
    await message.answer(text)

    if await crud_user.is_registered(message.from_user.id):
        return

    await continue_registration(message)


async def continue_registration(message: types.Message):
    registration_procedure = {
        User.place_residence.key: _("Where do you live? Please write your country and city names, e.g. New York, US"),
        User.normal_distance.key: _("Which distance you typically ride(in kilometres)?"),
        User.normal_speed.key: _("What speed do you ride most often?"),
    }

    column = await crud_user.next_need_column(message.from_user.id)

    if column is None:
        await message.answer(_("Registration passed!"))
    else:
        await message.answer(registration_procedure.get(column.key))


@dp.message_handler(not_registered)
async def registration(message: types.Message):
    column = await crud_user.next_need_column(message.from_user.id)

    if column is None:
        return

    value = await check_value(message, column, message.text)

    if value is None:
        return

    await crud_user.update(message.from_user.id, **{column.key: value})
    await continue_registration(message)
