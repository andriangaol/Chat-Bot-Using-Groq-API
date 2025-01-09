import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from routing import process_query

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Command handler for start
async def start(update: Update, context):
    await update.message.reply_text("Selamat datang! Saya adalah chatbot Anda. Tanyakan apa saja!")

# Message handler for incoming messages
async def handle_message(update: Update, context):
    user_message = update.message.text
    result = process_query(user_message)
    response = result["response"]
    await update.message.reply_text(response)

# Main function to run the bot
def main():
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("Bot Telegram sedang berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
