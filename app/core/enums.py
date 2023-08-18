from enum import StrEnum

__all__ = ("RouteTag",)


class RouteTag(StrEnum):
    """Tags used to classify API routes"""

    ORDER_CHANNELS = "🧷 Telegram Channels"
    ORDER_MESSAGES = "✉️ Telegram Order Messages"
    ORDER_RENDERS = " 🔪 Order Render Templates"
    AUTH = "🤷🏿‍♀️‍ Auth"
    CLOSE = "Close Order"
