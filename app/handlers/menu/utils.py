from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Jinja as Jinja_dialog

from app.services.render import flows as render_flows

from . import states


async def to_main(manager: DialogManager, **_kwargs) -> None:
    await manager.switch_to(states.Main.MAIN)


MAIN_MENU_BUTTON = Button(text=Const("☰ Main menu"), on_click=to_main, id="__main__")  # type: ignore


class Jinja(Jinja_dialog):
    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        return render_flows.user(self.template_text, data["user"], data=data)
