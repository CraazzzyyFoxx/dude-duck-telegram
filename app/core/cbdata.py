from aiogram.filters.callback_data import CallbackData


class OrderRespondCallback(CallbackData, prefix="ro"):
    order_id: str
    preorder: bool


class OrderRespondTimedCallback(CallbackData, prefix="rto"):
    order_id: str
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="ocy"):
    order_id: str
    state: bool
    preorder: bool


class OrderRespondConfirmCallback(CallbackData, prefix="oac"):
    order_id: str
    user_id: str
    preorder: bool
