from app.services.api.models import TelegramUser
from app.services.channel.models import Channel
from app.services.message.models import Message
from app.services.render.models import RenderConfig


def get_beanie_models():
    return [TelegramUser, Message, Channel, RenderConfig]
