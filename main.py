import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from bot_commands import (
    start, subscribe, unsubscribe, status, monitor_command, like_notification, 
    dislike_notification, handle_message, setup_periodic_monitoring
)
from config import TELEGRAM_TOKEN

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    """Инициализация после запуска бота"""
    await setup_periodic_monitoring(application)

def main() -> None:
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не установлен! Проверьте файл .env")
        return

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("monitor", monitor_command))
    application.add_handler(CommandHandler("like", like_notification))
    application.add_handler(CommandHandler("dislike", dislike_notification))

    # Обработка текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()