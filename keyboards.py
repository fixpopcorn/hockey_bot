from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Тренировочный комплект", callback_data="train")],
        [InlineKeyboardButton("Тёмный игровой", callback_data="dark")],
        [InlineKeyboardButton("Белый игровой", callback_data="white")],
    ]
    return InlineKeyboardMarkup(keyboard)
