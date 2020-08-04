from aiogram import filters, types
from app.core.bot import dp
from app.core.language import _  # noqa
from app.crud import crud_user
from app.utils import not_registered, check_value, registration_messages


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

    await registration_messages(message.from_user.id)


@dp.message_handler(not_registered)
async def registration(message: types.Message):
    column = await crud_user.next_need_column(message.from_user.id)

    if column is None:
        return

    try:
        value = await check_value(column, message.text)
    except Exception as exc:
        await message.answer(exc.args[0])
        return

    if value is None:
        return

    await crud_user.update(message.from_user.id, **{column.key: value})
    await registration_messages(message.from_user.id)
