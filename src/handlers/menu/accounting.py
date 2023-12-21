from aiogram_dialog import DialogManager, Window

from src.services.api import flows as api_flows

from . import states
from .utils import MAIN_MENU_BUTTON, Jinja


async def get_data_acc(dialog_manager: DialogManager, **_kwargs) -> dict:
    user = dialog_manager.middleware_data["user"]
    data = await api_flows.get_me_accounting(user)
    return {"acc": data, "user": user}


acc_window = Window(
    Jinja("menu_accounting"),
    MAIN_MENU_BUTTON,
    state=states.Main.ACC,
    getter=get_data_acc,
)
