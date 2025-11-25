import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from db import init_db
from handlers import take, list_records, button_click
from telegram import BotCommand

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- установка команд в Telegram ---
async def set_commands(app):
    commands = [
        BotCommand("take", "Взять комплект"),
        BotCommand("list", "Показать последние записи"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    # Инициализация базы данных
    init_db()

    # Создание приложения
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- вызываем set_commands через post_init ---
    async def on_startup(app):
        await set_commands(app)

    app.post_init = on_startup  # корутина выполнится один раз при старте

    # Добавляем хендлеры
    app.add_handler(CommandHandler("take", take))
    app.add_handler(CommandHandler("list", list_records))
    app.add_handler(CallbackQueryHandler(button_click))

    # Запуск бота (run_polling управляет event loop)
    app.run_polling()


if __name__ == "__main__":
    main()
