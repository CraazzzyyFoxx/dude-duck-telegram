from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Jinja as Jinja_dialog

from app.services.render import flows as render_flows

from . import states


async def to_main(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(states.Main.MAIN)


MAIN_MENU_BUTTON = Button(
    text=Const("☰ Main menu"),
    on_click=to_main,
    id="__main__"
)


class Jinja(Jinja_dialog):
    async def _render_text(
            self, data: dict, manager: DialogManager,
    ) -> str:
        return render_flows.user(self.template_text, data["user"].user, data=data)
