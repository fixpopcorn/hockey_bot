from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    insert_record, get_last_records,
    get_active_holder, close_active_records,
    delete_record, activate_previous_record, _connect
)

from keyboards import (
    main_keyboard,
    take_menu_keyboard,
    confirm_keyboard,
    back_to_main_keyboard,
    list_menu_keyboard
)

from datetime import datetime


UNIFORM_MAP = {
    "train": "тренировочный",
    "dark": "тёмный игровой",
    "white": "белый игровой",
}


def _fmt_ts(ts):
    """Форматирование timestamp."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%H:%M %d-%m-%Y")
    except Exception:
        return ts


# ---------- Команды ----------

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=main_keyboard())


async def take_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите комплект:",
        reply_markup=take_menu_keyboard()
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Меню списка записей:",
        reply_markup=list_menu_keyboard()
    )


async def holders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Тренировочный", callback_data="h:train")],
        [InlineKeyboardButton("Тёмный игровой", callback_data="h:dark")],
        [InlineKeyboardButton("Белый игровой", callback_data="h:white")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back:main")]
    ])
    await update.message.reply_text("Выберите комплект:", reply_markup=kb)


# ---------- CALLBACK HANDLER ----------

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # --- Главное меню: Взять комплект ---
    if data == "menu:take":
        await query.edit_message_text(
            "Выберите комплект:",
            reply_markup=take_menu_keyboard()
        )
        return

    # --- Отмена ---
    if data == "cancel:main":
        try:
            await query.delete_message()
        except Exception:
            await query.edit_message_text("Отменено.")
        return

    # --- Назад в главное меню ---
    if data == "back:main":
        await query.edit_message_text("Главное меню:", reply_markup=main_keyboard())
        return

    # --- Меню списка записей ---
    if data == "menu:list":
        await query.edit_message_text("Меню списка записей:", reply_markup=list_menu_keyboard())
        return

    # --- Меню holders ---
    if data == "menu:holders":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Тренировочный", callback_data="h:train")],
            [InlineKeyboardButton("Тёмный игровой", callback_data="h:dark")],
            [InlineKeyboardButton("Белый игровой", callback_data="h:white")],
            [InlineKeyboardButton("⬅ Назад", callback_data="back:main")]
        ])
        await query.edit_message_text("Выберите комплект:", reply_markup=kb)
        return

    # --- Показать, кто держит комплект ---
    if data.startswith("h:"):
        key = data.split(":", 1)[1]
        uniform_type = UNIFORM_MAP.get(key, "неизвестный")

        row = get_active_holder(uniform_type)
        if row:
            record_id, user, ts = row
            await query.edit_message_text(
                f"⚠️ Сейчас {uniform_type} комплект у: {user} (с {_fmt_ts(ts)})",
                reply_markup=back_to_main_keyboard()
            )
        else:
            await query.edit_message_text(
                f"⭐ {uniform_type} комплект свободен.",
                reply_markup=back_to_main_keyboard()
            )
        return

    # --- Выбор комплекта (u:train/dark/white) ---
    if data.startswith("u:"):
        key = data.split(":", 1)[1]
        uniform_type = UNIFORM_MAP.get(key, "неизвестный")

        row = get_active_holder(uniform_type)
        if row:
            record_id, holder, ts = row
            info = f"⚠ Сейчас {uniform_type} комплект у: {holder} (с {_fmt_ts(ts)})"
        else:
            info = f"⭐ {uniform_type} комплект свободен."

        context.user_data["pending_uniform"] = uniform_type

        await query.edit_message_text(
            f"{info}\n\nПодтвердите получение комплекта {uniform_type}:",
            reply_markup=confirm_keyboard()
        )
        return

    # --- Подтверждение взятия ---
    if data == "confirm:take":
        if "pending_uniform" not in context.user_data:
            await query.edit_message_text(
                "Ошибка: нет выбранного комплекта.",
                reply_markup=back_to_main_keyboard()
            )
            return

        uniform_type = context.user_data.pop("pending_uniform")
        user = query.from_user.username or query.from_user.full_name or "Unknown"

        close_active_records(uniform_type)
        insert_record(user, uniform_type)

        last = get_active_holder(uniform_type)
        if last:
            record_id, holder, ts = last
            await query.edit_message_text(
                f"Записано! {holder} взял {uniform_type} комплект.\n"
                f"ID {record_id}, {_fmt_ts(ts)}",
                reply_markup=back_to_main_keyboard()
            )
        else:
            await query.edit_message_text("Записано.", reply_markup=back_to_main_keyboard())
        return

    # --- Показать последние записи ---
    if data == "list:show":
        rows = get_last_records(limit=50)

        if not rows:
            await query.edit_message_text("Записей нет.", reply_markup=back_to_main_keyboard())
            return

        text = "Последние записи:\n\n"
        for record_id, user, uniform_type, ts, active in rows:
            status = "✔️ актив" if active else "❌ закрыта"
            text += f"ID {record_id}: {_fmt_ts(ts)} — {user}: {uniform_type} ({status})\n"

        await query.edit_message_text(text, reply_markup=back_to_main_keyboard())
        return

    # --- Удаление: выбор записи ---
    if data == "list:delete":
        rows = get_last_records(limit=50)

        if not rows:
            await query.edit_message_text("Нет записей для удаления.", reply_markup=back_to_main_keyboard())
            return

        kb = []
        for record_id, user, uniform_type, ts, active in rows:
            label = f"ID {record_id}: {user} — {uniform_type}"
            kb.append([InlineKeyboardButton(label, callback_data=f"del:{record_id}")])

        kb.append([InlineKeyboardButton("⬅ Назад", callback_data="back:main")])

        await query.edit_message_text(
            "Выберите запись для удаления:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # --- Подтверждение удаления ---
    if data.startswith("del:"):
        record_id = data.split(":", 1)[1]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Да, удалить", callback_data=f"del_confirm:{record_id}")],
            [InlineKeyboardButton("Отмена", callback_data="back:main")],
        ])
        await query.edit_message_text(
            f"Удалить запись ID {record_id}?",
            reply_markup=kb
        )
        return

    # --- Выполнение удаления + восстановление предыдущей записи ---
    if data.startswith("del_confirm:"):
        record_id = data.split(":", 1)[1]

        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT uniform_type FROM laundry WHERE id = ?", (record_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            await query.edit_message_text("Запись уже удалена.", reply_markup=back_to_main_keyboard())
            return

        uniform_type = row[0]

        delete_record(record_id)
        activate_previous_record(uniform_type)

        await query.edit_message_text(
            f"Запись ID {record_id} удалена.\n"
            f"Комплект «{uniform_type}» восстановлен к предыдущему состоянию.",
            reply_markup=back_to_main_keyboard()
        )
        return

    # --- Fallback ---
    await query.edit_message_text("Неизвестное действие.", reply_markup=back_to_main_keyboard())
