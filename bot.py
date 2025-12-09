import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler
)
from config import BOT_TOKEN
from db import init_db
from handlers import (
    menu, take_command, list_command, holders_command,
    button_click
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # команды
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("take", take_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("holders", holders_command))

    # inline callback handler (все inline кнопки)
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()


if __name__ == "__main__":
    main()
