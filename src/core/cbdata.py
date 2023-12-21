from aiogram.filters.callback_data import CallbackData


class OrderRespondCallback(CallbackData, prefix="ro"):
    order_id: int
    preorder: bool


class OrderRespondTimedCallback(CallbackData, prefix="rto"):
    order_id: int
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="ocy"):
    order_id: int
    state: bool
    preorder: bool


class OrderRespondConfirmCallback(CallbackData, prefix="oac"):
    order_id: int
    user_id: int
    preorder: bool
    state: bool


class VerifyCallback(CallbackData, prefix="vr"):
    user_id: int
    state: bool
