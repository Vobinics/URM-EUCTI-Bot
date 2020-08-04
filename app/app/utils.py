from aiogram import types
from app.core.language import _
from app.crud import crud_user
from sqlalchemy import Column, String, Integer


async def not_registered(message: types.Message) -> bool:
    return not await crud_user.is_registered(message.from_user.id)


def is_wait(line: Column, column: Column):
    return line.key == column.key


async def check_value(message: types.Message, column: Column, value: str):
    try:
        if isinstance(column.type, String):
            max_length = column.type.length
            if max_length < len(value):
                raise Exception(
                    _("The maximum allowed length for this value is {max_length} characters").format(
                        max_length=max_length)
                )
        elif isinstance(column.type, Integer):
            if value.isdigit():
                value = int(value)
            else:
                raise Exception(_("The entered value is not an integer"))
    except Exception as exc:
        await message.answer(exc.args[0])
    else:
        return value
