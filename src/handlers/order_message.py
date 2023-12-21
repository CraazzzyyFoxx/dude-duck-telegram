from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from src import models, schemas
from src.services.render import flows as render_flows

router = Router()


class Switch(StatesGroup):
    MAIN = State()


async def on_finish(callback: CallbackQuery, _: Button, manager: DialogManager) -> None:
    if manager.is_preview():
        await manager.done()
        return
    await callback.message.delete()
    if msg := manager.start_data.get("message"):
        await msg.delete()
    await manager.done()


async def get_data(dialog_manager: DialogManager, **_kwargs) -> dict:
    if dialog_manager.start_data is None:
        await dialog_manager.done()
        return {}

    dialog_manager.dialog_data["order_id"] = dialog_manager.start_data.get("order_id")
    dialog_manager.dialog_data["message"] = dialog_manager.start_data.get("message")
    user: models.UserDB = dialog_manager.middleware_data["user"]
    rendered_order = await render_flows.get_order_text(
        user,
        dialog_manager.dialog_data["order_id"],
        dialog_manager.find("preorder_option").is_checked(),
        dialog_manager.find("gold_option").is_checked(),
        dialog_manager.find("credentials_option").is_checked(),
    )
    return {
        "user": user,
        "message": dialog_manager.start_data.get("message"),
        "rendered_order": rendered_order,
        "lang": "🇺🇸" if user.language == schemas.UserLanguage.EN else "🇷🇺",
    }


input_window = Window(
    Format("{rendered_order}"),
    Checkbox(
        Const("✓ Preorder"),
        Const("Preorder"),
        id="preorder_option",
    ),
    Checkbox(
        Const("✓ Gold"),
        Const("Gold"),
        id="gold_option",
    ),
    Checkbox(
        Const("✓ Credentials"),
        Const("Credentials"),
        id="credentials_option",
    ),
    Button(
        text=Const("👋 See you"),
        id="good_bye",
        on_click=on_finish,
    ),
    state=Switch.MAIN,
    getter=get_data,
)


router.include_router(Dialog(input_window))


@router.message(Command("order_text"), flags={"chat_action": {"is_superuser"}})
async def get_id(
    message: types.Message,
    command: CommandObject,
    dialog_manager: DialogManager,
) -> None:
    if command.args is None:
        await message.answer("Error: You must provide an order id. Example: /order_message 500")
        return
    try:
        order_id = int(command.args)
    except ValueError:
        await message.answer("Error: You must provide an order id. Example: /order_message 500")
        return
    await dialog_manager.start(Switch.MAIN, data={"message": message, "order_id": order_id})
