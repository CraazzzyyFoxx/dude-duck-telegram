from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Jinja as Jinja_dialog

from src.services.render import flows as render_flows

from . import states


async def to_main(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.switch_to(states.Main.MAIN)


MAIN_MENU_BUTTON = Button(text=Const("☰ Main menu"), on_click=to_main, id="__main__")  # type: ignore


class Jinja(Jinja_dialog):
    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        return render_flows.user(self.template_text, data["middleware_data"]["user"], data=data)


class JinjaOrder(Jinja_dialog):
    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        rendered = render_flows.user(self.template_text, data["middleware_data"]["user"], data=data)
        if data["order"] is not None:
            order_text = await render_flows.get_order_text(
                data["middleware_data"]["user"], data["order"].id, with_credentials=True
            )
            rendered = rendered.format(rendered_order=order_text)
        return rendered.format(rendered_order="")
