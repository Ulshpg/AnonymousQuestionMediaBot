from aiogram.dispatcher.filters.state import State, StatesGroup


class User(StatesGroup):
    write = State()
    answer = State()

class Payment(StatesGroup):
    pay = State()
    check = State()