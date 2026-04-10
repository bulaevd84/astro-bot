from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
)
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

NAME, TOPIC, PROBLEM, FORMAT, BIRTH, PHONE = range(6)


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

    button = KeyboardButton("Отправить номер", request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        [[button]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await query.message.reply_text(
        "Оставьте номер телефона для связи 📱\n\n"
        "С телефона  - отправить номер кнопкой ниже.\n"
        "С компьютера — введите номер сообщением.",
        reply_markup=keyboard,
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user and user.username else "не указан"

    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text

    context.user_data["phone"] = phone_number

    text = f"""Новая заявка:

Имя: {context.user_data.get("name", "")}
Telegram: {username}
Телефон: {context.user_data.get("phone", "")}
Запрос: {context.user_data.get("topic", "")}
Описание: {context.user_data.get("problem", "")}
Формат: {context.user_data.get("format", "")}
Время рождения: {context.user_data.get("birth", "")}
"""

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    await update.message.reply_text(
        "Спасибо! Татьяна свяжется с вами 👌",
        reply_markup=ReplyKeyboardRemove(),
    )
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
            PHONE: [MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, phone)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
