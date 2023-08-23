from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram_dialog import StartMode, DialogManager, Dialog, Window, LaunchMode

from aiogram_dialog.widgets.kbd import Button, WebApp
from aiogram_dialog.widgets.text import Const, Format

from app.core import config
from app.services.api import models as api_models

from .states import Main
from .utils import Jinja
from .accounting import acc_window
from .orders import orders_window, ID_STUB_SCROLL

router = Router()


async def on_finish(callback: CallbackQuery, _: Button, manager: DialogManager):
    if manager.is_preview():
        await manager.done()
        return
    await callback.message.delete()
    if msg := manager.start_data.get("message"):
        await msg.delete()
    await manager.done()


async def get_data(dialog_manager: DialogManager, **_kwargs):
    if dialog_manager.start_data is None:
        await dialog_manager.done()
        return
    user = dialog_manager.start_data.get("user", None)
    dialog_manager.dialog_data["user"] = user
    dialog_manager.dialog_data["message"] = dialog_manager.start_data.get("message")
    return {"user": user, "message": dialog_manager.start_data.get("message"), "auth_url": config.app.auth_url}


async def to_acc(callback: CallbackQuery, _: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(Main.ACC)


async def to_orders(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.start_data is None:
        await dialog_manager.done()
        return
    if button.widget_id == "active_orders":
        status = api_models.OrderSelection.InProgress
    else:
        status = api_models.OrderSelection.Completed
    await dialog_manager.find(ID_STUB_SCROLL).set_page(0)
    dialog_manager.dialog_data["orders"] = status
    if dialog_manager.dialog_data.get("orders_data"):
        dialog_manager.dialog_data.pop("orders_data")
    await dialog_manager.switch_to(Main.ORDERS)


main_dialog = Dialog(
    Window(
        Jinja("menu"),
        Button(
            text=Const("📊 Balance"),
            id="accounting",
            on_click=to_acc,
        ),
        Button(
            text=Format("📋 Active orders"),
            id="active_orders",
            on_click=to_orders,
        ),
        Button(
            text=Format("📂 Completed orders"),
            id="completed_orders",
            on_click=to_orders,
        ),
        WebApp(
            text=Const("🧷 Close order"),
            url=Format("{auth_url}order/close?user_id={message.from_user.id}"),
            id="close_order",
        ),
        Button(
            text=Const("👋 See you"),
            id="good_bye",
            on_click=on_finish,
        ),
        getter=get_data,
        state=Main.MAIN,
    ),
    acc_window,
    orders_window,
    launch_mode=LaunchMode.SINGLE_TOP,
)

router.include_router(main_dialog)


@router.message(Command('menu'), flags={'chat_action': {"is_private"}})
async def menu(message: types.Message, dialog_manager: DialogManager, user) -> None:
    await dialog_manager.start(Main.MAIN, data={"message": message, "user": user},
                               mode=StartMode.NORMAL)
