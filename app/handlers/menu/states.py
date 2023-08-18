from aiogram.fsm.state import State, StatesGroup


class Accounting(StatesGroup):
    MAIN = State()
    DEFAULT_PAGER = State()
    PAGERS = State()
    TEXT = State()
    STUB = State()


class Main(StatesGroup):
    MAIN = State()
    ORDERS = State()
    ACC = State()
    ACO = State()
    CDO = State()


class ActiveOrders(StatesGroup):
    MAIN = State()
    ROW = State()
    COLUMN = State()
    GROUP = State()


class CompletedOrders(StatesGroup):
    MAIN = State()
    SELECT = State()
    RADIO = State()
