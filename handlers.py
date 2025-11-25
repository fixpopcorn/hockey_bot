from telegram import Update
from telegram.ext import ContextTypes
from db import insert_record, get_last_records, get_current_holder_by_type
from keyboards import main_keyboard, holders_keyboard


async def take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    await context.bot.send_message(
        chat_id=user_id,
        text="Выберите комплект, который вы взяли стирать:",
        reply_markup=main_keyboard()
    )

async def list_records(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    rows = get_last_records()

    if not rows:
        await update.message.reply_text("Записей нет.")
        return

    text = "Последние записи:\n\n"
    for user, uniform_type, ts in rows:
        text += f"{ts} — {user}: {uniform_type}\n"

    await update.message.reply_text(text)

async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    await update.message.reply_text(
        "Выберите комплект, чтобы узнать, у кого он сейчас:",
        reply_markup=holders_keyboard()
    )



async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.delete_message()
        return

    if query.data.startswith("holder_"):
        uniform_map = {
            "holder_train": "тренировочный",
            "holder_white": "белый игровой",
            "holder_dark": "тёмный игровой",
        }
        uniform_type = uniform_map.get(query.data)
        if uniform_type:
            row = get_current_holder_by_type(uniform_type)
            if row:
                user, ts = row
                text = f"{uniform_type}: {user} (взял {ts})"
            else:
                text = f"{uniform_type}: сейчас никто не взял комплект."
            await query.edit_message_text(text)
        return


    uniform_map = {
        "train": "тренировочный",
        "dark": "тёмный игровой",
        "white": "белый игровой",
    }
    if query.data in uniform_map:
        uniform_type = uniform_map.get(query.data, "неизвестный")
        user = query.from_user.username or query.from_user.full_name or "Unknown"
    insert_record(user, uniform_type)
    await query.edit_message_text(
        f"Записано! {user} взял {uniform_type} комплект."
    )
