from aiogram import filters
from aiogram.types import (Message, CallbackQuery, ParseMode, BotCommand, ReplyKeyboardMarkup, KeyboardButton,
                           ContentType, ChatActions)
from app.core.bot import dp, bot
from app.core.config import settings
from app.core.language import _  # noqa
from app.crud import crud_user, crud_task
from app.keyboards import task_keyboard
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

    user = await crud_user.get_or_create(message.from_user.id)
    if task_id in user.done_tasks:
        status = _('Done')
        keyboard = await task_keyboard(task['example_road'], only_example_road=True)
    elif task_id == user.proceed_task:
        status = _('In work')
        keyboard = await task_keyboard(task['example_road'])
    else:
        status = _('Not performed')
        keyboard = await task_keyboard(task['example_road'], task_id)

    text = _(
        "*Task {task_id}*\n"
        "Status: {status}\n\n"
        "*Task description*\n"
        "Drive along {road_type} with slides and slopes at an angle of no more than {permissible_angle} degrees. "
        "Start should be with a full battery charge, and stop at {charge_percentage} percentage of the battery. "
        "Speed should be within {need_speed} km/h. The trip should be recorded to a file using the WheelLog "
        "program. If you have an iOS device, use the EUCWorld application. In the report, along with the file, "
        "write which unicycle you drove"
    ).format(**task, task_id=task_id, status=status)

    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(menu('task', 0))
async def proceed_task_handler(callback_query: CallbackQuery):
    parsed_menu = await menu_parser(callback_query.data)

    if parsed_menu[1] == 'refuse':
        task_id = await crud_user.unset_proceed_task(callback_query.from_user.id)

        if task_id is None:
            await callback_query.answer()
            return

        task = await crud_task.get(task_id)
        keyboard = await task_keyboard(task['example_road'], task_id)
        await callback_query.message.edit_reply_markup(keyboard)

        await callback_query.answer(_("Task refused"))

    elif await crud_task.exists(parsed_menu[1]):
        done_tasks = await crud_user.get_done_tasks(callback_query.from_user.id)
        task_id = await crud_user.set_proceed_task(callback_query.from_user.id, parsed_menu[1])

        if task_id in done_tasks:
            await callback_query.answer(_("This task has already been completed"))
            return

        task = await crud_task.get(task_id)

        keyboard = await task_keyboard(task['example_road'])
        await callback_query.message.edit_reply_markup(keyboard)

        await callback_query.answer(_("This task is marked as in progress"))

    else:
        await callback_query.answer(_("Task with this id does not exist"))


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def report_handler(message: Message):
    if message.document.mime_type != 'text/comma-separated-values':
        await message.answer(_('Invalid file format! Need a file in csv format'))
        return

    if message.caption is None:
        await message.answer(_('The submitted file has no signature with the electric unicycle model'))
        return

    await message.answer(_('Thanks for your input!'))

    user = await crud_user.get_or_create(message.from_user.id)
    await crud_user.add_done_task(message.from_user.id, user.proceed_task)
    await crud_user.unset_proceed_task(message.from_user.id)

    format_data = dict(
        task_id=user.proceed_task,
        user_name=message.from_user.full_name,
        user_id=message.from_user.id,
        caption=message.caption
    )

    text = _(
        "*Task {task_id}*\n"
        "User: [{user_name}](tg://user?id={user_id})\n"
        "Message: {caption}"
    ).format(**format_data)

    await bot.send_chat_action(settings.CHAT_ID, ChatActions.UPLOAD_DOCUMENT)
    await bot.send_document(settings.CHAT_ID, message.document.file_id, caption=text, parse_mode=ParseMode.MARKDOWN)
