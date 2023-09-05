from aiogram.filters.callback_data import CallbackData
from beanie import PydanticObjectId


class OrderRespondCallback(CallbackData, prefix="ro"):
    order_id: PydanticObjectId
    preorder: bool


class OrderRespondTimedCallback(CallbackData, prefix="rto"):
    order_id: PydanticObjectId
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="ocy"):
    order_id: PydanticObjectId
    state: bool
    preorder: bool


class OrderRespondConfirmCallback(CallbackData, prefix="oac"):
    order_id: PydanticObjectId
    user_id: PydanticObjectId
    preorder: bool
