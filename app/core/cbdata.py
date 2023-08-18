from aiogram.filters.callback_data import CallbackData
from beanie import PydanticObjectId


class OrderRespondCallback(CallbackData, prefix="ro"):
    order_id: PydanticObjectId


class OrderRespondTimedCallback(CallbackData, prefix="rto"):
    order_id: PydanticObjectId
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="ocy"):
    order_id: PydanticObjectId
    state: bool


class OrderRespondConfirmCallback(CallbackData, prefix="oac"):
    order_id: PydanticObjectId
    user_id: PydanticObjectId
