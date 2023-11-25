from aiogram.types import Message
from aiogram_dialog import DialogManager, Window

from src.services.api import flows as api_flows

from . import states
from .utils import MAIN_MENU_BUTTON, Jinja


async def get_data_acc(dialog_manager: DialogManager, **_kwargs) -> dict:
    d: Message = dialog_manager.dialog_data.get("message", None)
    user = dialog_manager.dialog_data.get("user", None)
    data = await api_flows.get_me_accounting(d.from_user.id)
    return {"acc": data, "user": user}


acc_window = Window(Jinja("menu_accounting"), MAIN_MENU_BUTTON, state=states.Main.ACC, getter=get_data_acc)
