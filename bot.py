from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8659826917:AAHP9yPM2GMjQV2Bb88ZSNVBdt2TKiYMv0k"
ADMIN_CHAT_ID = 792501571

NAME, TOPIC, PROBLEM, FORMAT, BIRTH, READY = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Как тебя зовут?")
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Деньги и карьера", callback_data="Деньги и карьера")],
        [InlineKeyboardButton("Отношения", callback_data="Отношения")],
        [InlineKeyboardButton("Поиск себя", callback_data="Поиск себя")],
        [InlineKeyboardButton("Понять текущий период", callback_data="Понять текущий период")],
        [InlineKeyboardButton("Другое", callback_data="Другое")],
    ]

    await update.message.reply_text(
        "С чем вы хотите разобраться?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return TOPIC


async def topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["topic"] = query.data

    await query.message.reply_text("Опишите коротко, что сейчас происходит.")
    return PROBLEM


async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["problem"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Аудиоподкаст", callback_data="Аудиоподкаст")],
        [InlineKeyboardButton("Видеовстреча (Zoom)", callback_data="Zoom")],
        [InlineKeyboardButton("Пока не знаю", callback_data="Пока не знаю")],
    ]

    await update.message.reply_text(
        "Как вам удобнее получить разбор?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return FORMAT


async def format_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["format"] = query.data

    keyboard = [
        [InlineKeyboardButton("Да, точно", callback_data="Да, точно")],
        [InlineKeyboardButton("Примерно", callback_data="Примерно")],
        [InlineKeyboardButton("Нет", callback_data="Нет")],
    ]

    await query.message.reply_text(
        "Знаете ли вы своё время рождения?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return BIRTH


async def birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["birth"] = query.data

    keyboard = [
        [InlineKeyboardButton("Да", callback_data="Да")],
        [InlineKeyboardButton("Пока думаю", callback_data="Пока думаю")],
    ]

    await query.message.reply_text(
        "Готовы ли вы работать с рекомендациями после разбора?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return READY


async def ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    username = f"@{user.username}" if user and user.username else "не указан"
    context.user_data["ready"] = query.data

    text = f"""Новая заявка:

Имя: {context.user_data.get("name", "")}
Telegram: {username}
Запрос: {context.user_data.get("topic", "")}
Описание: {context.user_data.get("problem", "")}
Формат: {context.user_data.get("format", "")}
Время рождения: {context.user_data.get("birth", "")}
Готовность: {context.user_data.get("ready", "")}
"""

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    await query.message.reply_text("Готово! Татьяна напишет вам в Telegram 👌")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            TOPIC: [CallbackQueryHandler(topic)],
            PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, problem)],
            FORMAT: [CallbackQueryHandler(format_step)],
            BIRTH: [CallbackQueryHandler(birth)],
            READY: [CallbackQueryHandler(ready)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
