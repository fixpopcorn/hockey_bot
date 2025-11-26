import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from db import init_db
from handlers import take, list_menu, button_click, holders
from telegram import BotCommand

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def set_commands(app):
    commands = [
        BotCommand("take", "Взять комплект"),
        BotCommand("list", "Показать последние записи"),
        BotCommand("holders", "Узнать, у кого сейчас комплект")
    ]
    await app.bot.set_my_commands(commands)


def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    async def on_startup(app):
        await set_commands(app)

    app.post_init = on_startup 

    app.add_handler(CommandHandler("take", take))
    app.add_handler(CommandHandler("list", list_menu))
    app.add_handler(CommandHandler("holders", holders))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()


if __name__ == "__main__":
    main()
