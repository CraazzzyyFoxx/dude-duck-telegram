from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, LaunchMode, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, WebApp
from aiogram_dialog.widgets.text import Const, Format

from app.core import config
from app.services.api import flows as api_flows
from app.services.api import models as api_models
from app.services.api import schemas as api_schemas

from .accounting import acc_window
from .orders import ID_STUB_SCROLL, orders_window
from .states import Main
from .utils import Jinja

router = Router()


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

    if dialog_manager.dialog_data.get("user") is None:
        dialog_manager.dialog_data["user"] = dialog_manager.start_data.get("user")

    dialog_manager.dialog_data["message"] = dialog_manager.start_data.get("message")
    user = dialog_manager.dialog_data["user"]
    lang = "🇺🇸" if user.language == api_schemas.UserLanguage.EN else "🇷🇺"
    return {
        "user": user,
        "message": dialog_manager.start_data.get("message"),
        "auth_url": config.app.auth_url,
        "lang": lang,
    }


async def to_acc(dialog_manager: DialogManager, **_kwargs) -> None:
    await dialog_manager.switch_to(Main.ACC)


async def to_orders(button: Button, dialog_manager: DialogManager, **_kwargs) -> None:
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


async def change_language(callback: CallbackQuery, dialog_manager: DialogManager, **_kwargs) -> None:
    dialog_manager.dialog_data["user"] = await api_flows.change_language(callback.from_user.id)
    await dialog_manager.switch_to(Main.MAIN)


main_dialog = Dialog(
    Window(
        Jinja("menu"),
        Button(
            text=Const("📊 Balance"),
            id="accounting",
            on_click=to_acc,  # type: ignore
        ),
        Button(
            text=Format("📋 Active orders"),
            id="active_orders",
            on_click=to_orders,  # type: ignore
        ),
        Button(
            text=Format("📂 Completed orders"),
            id="completed_orders",
            on_click=to_orders,  # type: ignore
        ),
        WebApp(
            text=Const("🧷 Close order"),
            url=Format("{auth_url}bot/order/close?user_id={message.from_user.id}"),
            id="close_order",
        ),
        Button(
            text=Format("{lang} Language"),
            id="change_language",
            on_click=change_language,  # type: ignore
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


@router.message(Command("menu"), flags={"chat_action": {"is_private"}})
async def menu(message: types.Message, dialog_manager: DialogManager, user) -> None:
    await dialog_manager.start(Main.MAIN, data={"message": message, "user": user}, mode=StartMode.NORMAL)
