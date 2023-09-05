from aiogram_dialog import DialogManager, Window

from aiogram_dialog.widgets.kbd import Row, FirstPage, PrevPage, NextPage, LastPage, StubScroll, Button
from aiogram_dialog.widgets.text import Const, Format

from app.services.api import flows as api_flows

from . import states
from .utils import MAIN_MENU_BUTTON, Jinja

ID_STUB_SCROLL = "stub_scroll"


async def paging_getter_aco(dialog_manager: DialogManager, **_kwargs):
    current_page = await dialog_manager.find(ID_STUB_SCROLL).get_page()
    d = dialog_manager.dialog_data.get("message", None)
    user = dialog_manager.start_data.get("user", None)
    status = dialog_manager.dialog_data["orders"]
    orders = dialog_manager.dialog_data.get("orders_data", None)
    if not orders:
        orders = await api_flows.me_get_orders(d.from_user.id, status, page=1 + int(current_page / 10))
        dialog_manager.dialog_data["orders_data"] = orders
    if int(current_page / 10) + 1 != orders.page:
        orders = await api_flows.me_get_orders(d.from_user.id, status, page=1 + int(current_page / 10))
        dialog_manager.dialog_data["orders_data"] = orders

    return {
        "user": user,
        "pages": orders.total if orders.total > 0 else 1,
        "current_page": current_page + 1,
        "order": orders.results[current_page % orders.per_page] if orders.total > 0 else None,
    }


orders_window = Window(
    Jinja("menu_orders"),
    StubScroll(id=ID_STUB_SCROLL, pages="pages"),
    Row(
        FirstPage(
            scroll=ID_STUB_SCROLL, text=Const("⏮️"),
        ),
        PrevPage(
            scroll=ID_STUB_SCROLL, text=Const("◀️"),
        ),
        Button(
            text=Format("{current_page} in {pages}"),
            id=ID_STUB_SCROLL,
        ),
        NextPage(
            scroll=ID_STUB_SCROLL, text=Const("▶️"),
        ),
        LastPage(
            scroll=ID_STUB_SCROLL, text=Const("⏭️"),
        ),
    ),
    MAIN_MENU_BUTTON,
    getter=paging_getter_aco,
    state=states.Main.ORDERS,

)
