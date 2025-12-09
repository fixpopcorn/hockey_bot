from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Главное меню — компактное, только команды
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎽 Взять комплект", callback_data="menu:take")],
        [InlineKeyboardButton("📋 Список записей", callback_data="menu:list")],
        [InlineKeyboardButton("👥 Кто держит сейчас", callback_data="menu:holders")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel:main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню выбора комплекта
def take_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Тренировочный комплект", callback_data="u:train")],
        [InlineKeyboardButton("Тёмный игровой", callback_data="u:dark")],
        [InlineKeyboardButton("Белый игровой", callback_data="u:white")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back:main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Кнопки подтверждения
def confirm_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm:take")],
        [InlineKeyboardButton("⬅ Назад", callback_data="menu:take")]
    ])

# Меню списка записей
def list_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Показать все записи", callback_data="list:show")],
        [InlineKeyboardButton("🗑 Удалить запись", callback_data="list:delete")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back:main")],
    ])

# Назад в главное меню
def back_to_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Назад", callback_data="back:main")]
    ])
