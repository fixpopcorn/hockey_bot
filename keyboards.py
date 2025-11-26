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

def list_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Показать список", callback_data="show_list")],
        [InlineKeyboardButton("🗑 Удалить запись", callback_data="delete_select")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def delete_buttons(records):
    keyboard = []
    for rec_id, user, uniform_type, ts in records:
        text = f"{ts} — {user}: {uniform_type}"
        keyboard.append(
            [InlineKeyboardButton(f"❌ {text}", callback_data=f"del_{rec_id}")]
        )
    keyboard.append(
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_list")]
    )
    return InlineKeyboardMarkup(keyboard)