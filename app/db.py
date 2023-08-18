from app.services.api.models import TelegramUser
from app.services.channel.models import OrderChannel
from app.services.message.models import Message
from app.services.response.models import OrderResponse
from app.services.render.models import RenderConfig


def get_beanie_models():
    return [TelegramUser, Message, OrderChannel, OrderResponse, RenderConfig]
