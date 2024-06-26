from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, FirstPage, LastPage, NextPage, PrevPage, Row, StubScroll
from aiogram_dialog.widgets.text import Const, Format

from src.services.api import flows as api_flows

from . import states
from .utils import MAIN_MENU_BUTTON, JinjaOrder

ID_STUB_SCROLL = "stub_scroll"


async def paging_getter_aco(dialog_manager: DialogManager, **_kwargs) -> dict:
    current_page = await dialog_manager.find(ID_STUB_SCROLL).get_page()
    user = dialog_manager.middleware_data["user"]
    status = dialog_manager.dialog_data["orders"]
    orders = dialog_manager.dialog_data.get("orders_data", None)
    if not orders:
        orders = await api_flows.get_me_orders(user, status, page=1 + int(current_page / 10))
        dialog_manager.dialog_data["orders_data"] = orders
    if int(current_page / 10) + 1 != orders.page:
        orders = await api_flows.get_me_orders(user, status, page=1 + int(current_page / 10))
        dialog_manager.dialog_data["orders_data"] = orders

    return {
        "message": dialog_manager.dialog_data.get("message", None),
        "pages": orders.total if orders.total > 0 else 1,
        "current_page": current_page + 1,
        "order": orders.results[current_page % orders.per_page] if orders.total > 0 else None,
    }


orders_window = Window(
    JinjaOrder("menu_orders"),
    StubScroll(id=ID_STUB_SCROLL, pages="pages"),
    Row(
        FirstPage(
            scroll=ID_STUB_SCROLL,
            text=Const("⏮️"),
        ),
        PrevPage(
            scroll=ID_STUB_SCROLL,
            text=Const("◀️"),
        ),
        Button(
            text=Format("{current_page} in {pages}"),
            id=ID_STUB_SCROLL,
        ),
        NextPage(
            scroll=ID_STUB_SCROLL,
            text=Const("▶️"),
        ),
        LastPage(
            scroll=ID_STUB_SCROLL,
            text=Const("⏭️"),
        ),
    ),
    MAIN_MENU_BUTTON,
    getter=paging_getter_aco,
    state=states.Main.ORDERS,
)
