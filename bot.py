import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id] = {"photos": []}
    await update.message.reply_text("Привет! Введи Айди аккаунта:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if chat_id not in user_data:
        await update.message.reply_text("Напиши /start сначала.")
        return

    data = user_data[chat_id]
    if "id" not in data:
        data["id"] = text
        await update.message.reply_text("Теперь введи уровень:")
    elif "level" not in data:
        data["level"] = text
        await update.message.reply_text("Теперь введи цену:")
    elif "price" not in data:
        data["price"] = text
        await update.message.reply_text("Теперь введи контакт продавца:")
    elif "contact" not in data:
        data["contact"] = text
        await update.message.reply_text("Теперь отправь скриншоты (до 5). Когда закончишь — напиши /done")

async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_data:
        return
    photo = update.message.photo[-1]
    user_data[chat_id]["photos"].append(photo.file_id)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_data:
        await update.message.reply_text("Сначала напиши /start.")
        return

    data = user_data.pop(chat_id)
    text = (
        f"📥 Новая заявка:\n\n"
        f"🔹 Айди аккаунта: {data['id']}\n"
        f"🔹 Уровень: {data['level']}\n"
        f"💰 Цена: {data['price']}\n"
        f"📞 Контакт: {data['contact']}"
    )

    if data["photos"]:
        media = [InputMediaPhoto(photo_id) for photo_id in data["photos"][:5]]
        await context.bot.send_message(CHANNEL_ID, text)
        await context.bot.send_media_group(CHANNEL_ID, media)
    else:
        await context.bot.send_message(CHANNEL_ID, text)

    await update.message.reply_text("✅ Заявка отправлена!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
