from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

BOT_TOKEN = '7334470377:AAHltUJ6iYtwxEH-PrLEKonkwni8KBz8jhM'
CHANNEL_ID = -1002698499154  # Заменить на ID канала

# Этапы диалога
ID, LEVEL, PRICE, CONTACT, PHOTOS = range(5)

# Хранилище временных данных
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("?? Введите Айди аккаунта:")
    return ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id'] = update.message.text
    await update.message.reply_text("?? Введите уровень аккаунта:")
    return LEVEL

async def get_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['level'] = update.message.text
    await update.message.reply_text("?? Укажите цену:")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("?? Как с вами связаться (ник, тг и т.д.):")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    await update.message.reply_text("?? Отправьте скриншоты (макс 5). Когда закончите — напишите /done.")
    context.user_data['photos'] = []
    return PHOTOS

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id  # Последнее (лучшее) качество
    context.user_data['photos'].append(photo)
    if len(context.user_data['photos']) >= 5:
        return await done(update, context)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    caption = (
        f"?? Новая заявка:\n"
        f"?? Айди: {data['id']}\n"
        f"?? Уровень: {data['level']}\n"
        f"?? Цена: {data['price']}\n"
        f"?? Связь: {data['contact']}"
    )

    # Если есть фото
    if data.get('photos'):
        media = [InputMediaPhoto(media=photo, caption=caption if i == 0 else "") for i, photo in enumerate(data['photos'])]
        await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media)
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=caption)

    await update.message.reply_text("? Заявка отправлена в канал!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("? Заявка отменена.")
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
        LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_level)],
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        PHOTOS: [
            MessageHandler(filters.PHOTO, get_photo),
            CommandHandler("done", done)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv)

app.run_polling()
