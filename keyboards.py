from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Тренировочный комплект", callback_data="train")],
        [InlineKeyboardButton("Тёмный игровой", callback_data="dark")],
        [InlineKeyboardButton("Белый игровой", callback_data="white")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def holders_keyboard():
    keyboard = [
        [InlineKeyboardButton("Тренировочный", callback_data="holder_train")],
        [InlineKeyboardButton("Белый игровой", callback_data="holder_white")],
        [InlineKeyboardButton("Тёмный игровой", callback_data="holder_dark")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)
