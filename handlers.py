from telegram import Update
from telegram.ext import ContextTypes
from db import insert_record, get_last_records, get_current_holder_by_type, get_all_records, delete_record
from keyboards import main_keyboard, holders_keyboard, list_keyboard, delete_buttons
from config import ADMINS


async def take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    await update.message.reply_text(
        "Выберите комплект, который вы взяли стирать:",
        reply_markup=main_keyboard()
    )


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    await update.message.reply_text(
        "Выберите комплект, чтобы узнать, у кого он сейчас:",
        reply_markup=holders_keyboard()
    )


async def list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=list_keyboard()
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.delete_message()
        return

    if data == "show_list":
        rows = get_last_records()
        if not rows:
            await query.edit_message_text("Записей нет.", reply_markup=list_keyboard())
            return

        text = "Последние записи:\n\n"
        for user, uniform_type, ts in rows:
            text += f"{ts} — {user}: {uniform_type}\n"

        await query.edit_message_text(text, reply_markup=list_keyboard())
        return

    if data == "delete_select":
        if query.from_user.id not in ADMINS:
            await query.answer("Нет доступа.", show_alert=True)
            return

        rows = get_all_records()
        if not rows:
            await query.edit_message_text("Нет данных для удаления", reply_markup=list_keyboard())
            return

        await query.edit_message_text(
            "Выберите запись, которую удалить:",
            reply_markup=delete_buttons(rows)
        )
        return

    if data == "back_to_list":
        await query.edit_message_text("Выберите действие:", reply_markup=list_keyboard())
        return

    if data.startswith("del_"):
        if query.from_user.id not in ADMINS:
            await query.answer("Нет прав!", show_alert=True)
            return

        rec_id = int(data.split("_")[1])
        delete_record(rec_id)
        await query.edit_message_text("Запись удалена.", reply_markup=list_keyboard())
        return

    if data.startswith("holder_"):
        uniform_map = {
            "holder_train": "тренировочный",
            "holder_white": "белый игровой",
            "holder_dark": "тёмный игровой",
        }
        uniform_type = uniform_map[data]
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

    if data in uniform_map:
        uniform_type = uniform_map[data]
        user = query.from_user.username or query.from_user.full_name or "Unknown"
        insert_record(user, uniform_type)
        await query.edit_message_text(
            f"Записано! {user} взял {uniform_type} комплект."
        )
        return
