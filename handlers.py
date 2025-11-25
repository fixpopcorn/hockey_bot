from telegram import Update
from telegram.ext import ContextTypes
from db import insert_record, get_last_records
from keyboards import main_keyboard


async def take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите комплект, который вы взяли стирать:",
        reply_markup=main_keyboard()
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uniform_map = {
        "train": "тренировочный",
        "dark": "тёмный игровой",
        "white": "белый игровой",
    }

    uniform_type = uniform_map.get(query.data, "неизвестный")

    user = (
        query.from_user.username
        or query.from_user.full_name
        or "Unknown"
    )

    insert_record(user, uniform_type)

    await query.edit_message_text(
        f"Записано! {user} взял {uniform_type} комплект."
    )


async def list_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_last_records()

    if not rows:
        await update.message.reply_text("Записей нет.")
        return

    text = "Последние записи:\n\n"
    for user, uniform_type, ts in rows:
        text += f"{ts} — {user}: {uniform_type}\n"

    await update.message.reply_text(text)
