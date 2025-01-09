import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from routing import handle_message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    """Mengirim pesan saat command /start dijalankan."""
    welcome_message = """
    Halo! 👋 Saya adalah bot asisten yang bisa membantu Anda dengan:
    - Perhitungan matematika
    - Menjawab pertanyaan umum
    
    Silakan ajukan pertanyaan Anda!
    """
    await update.message.reply_text(welcome_message)

async def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    error_message = "Maaf, terjadi kesalahan. Silakan coba lagi nanti."
    if update.message:
        await update.message.reply_text(error_message)

def main():
    """Start the bot."""
    # Ambil token dari environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN tidak ditemukan di environment variables")
        return

    # Buat aplikasi
    application = Application.builder().token(token).build()

    # Tambahkan handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Tambahkan error handler
    application.add_error_handler(error_handler)

    # Mulai bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
