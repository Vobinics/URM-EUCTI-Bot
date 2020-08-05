from aiogram import filters
from aiogram.types import (Message, CallbackQuery, ParseMode, BotCommand, ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from app.core.bot import dp
from app.core.language import _  # noqa
from app.crud import crud_user, crud_task
from app.utils import (not_registered, check_value, registration_messages, task_parser, is_admin, is_task, menu,
                       menu_parser)


@dp.message_handler(filters.CommandStart())
async def start(message: Message):
    # Welcome
    text = _("Hello! With this bot, you can subscribe to the EUC Testing Initiative for UniRoadMap to help us create "
             "a really polished and good product! Your data will be used to create unique settings for each EUC model "
             "for our navigation engine. Every personal information about you is stored securely and no one except "
             "our developers can access it.")
    await message.answer(text)

    if await crud_user.is_registered(message.from_user.id):
        await tasks_handler(message)
    else:
        await registration_messages(message.from_user.id)


@dp.message_handler(filters.Command('cmd-set'), is_admin)
async def set_commands(message: Message):
    commands = [
        BotCommand(command="/start", description="Start"),
        BotCommand(command="/tasks", description="Allow tasks")
        # BotCommand(command="/execution", description="Task in execution")
    ]
    await message.bot.set_my_commands(commands)
    await message.answer("Commands set up!")


@dp.message_handler(not_registered)
async def registration(message: Message):
    column = await crud_user.next_need_column(message.from_user.id)

    if column is None:
        return

    try:
        value = await check_value(column, message.text)
    except Exception as exc:
        await message.answer(exc.args[0])
        return

    if value is None:
        await tasks_handler(message)
        return

    user = await crud_user.get_or_create(message.from_user.id)
    await crud_user.update(user, **{column.key: value})

    success = await registration_messages(message.from_user.id)
    if success:
        await tasks_handler(message)


@dp.message_handler(filters.Command('tasks'))
async def tasks_handler(message: Message):
    tasks = await crud_task.get_all()

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        num = task['id']
        button = KeyboardButton(f"{_('Task')} {num}")
        keyboard.add(button)

    await message.answer(_("*Allow tasks*"), parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


@dp.message_handler(is_task)
async def task_handler(message: Message):
    task_id = await task_parser(message.text)
    task = await crud_task.get(task_id)

    if task is None:
        await message.answer(_("Task with this id does not exist"))
        return

    text = _("Drive along {road_type} with slides and slopes at an angle of no more than {permissible_angle} degrees. "
             "Start should be with a full battery charge, and stop at {charge_percentage} percentage of the battery. "
             "Speed should be within {need_speed} km/h. The trip should be recorded to a file using the WheelLog "
             "program. If you have an iOS device, use the EUCWorld application. In the report, along with the file, "
             "write which unicycle you drove.")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(_('Example road'), url=task['example_road']))
    keyboard.add(InlineKeyboardButton(_('Proceed with!'), callback_data=f'proceed/{task_id}/set'))

    await message.answer(text.format(**task), reply_markup=keyboard)


@dp.callback_query_handler(menu('proceed', 0), menu('set', -1))
async def set_proceed_task_handler(callback_query: CallbackQuery):
    task_id: int = (await menu_parser(callback_query.data))[1]

    if await crud_task.exists(task_id):
        await crud_user.set_proceed_task(callback_query.from_user.id, task_id)
        await callback_query.answer(_("This task is marked as in progress"))
        return

    await callback_query.answer(_("Task with this id does not exist"))
