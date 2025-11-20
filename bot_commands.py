import logging
from telegram import Update
from telegram.ext import ContextTypes, Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from subscription_manager import SubscriptionManager
from monitor import Monitor
from ai_analyzer import analyze_changes_for_user, adapt_notifications
from user_preferences import UserPreferences
from config import CHECK_INTERVAL_MINUTES

logger = logging.getLogger(__name__)

subscription_manager = SubscriptionManager()
monitor = Monitor()
user_preferences = UserPreferences()
scheduler = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Добро пожаловать! Используйте команды:\n"
        "/subscribe - подписаться на уведомления\n"
        "/unsubscribe - отписаться от уведомлений\n"
        "/status - проверить статус мониторинга\n"
        "/monitor [url] - начать мониторинг сайта\n"
        "/like - оценить последнее уведомление как полезное\n"
        "/dislike - оценить последнее уведомление как бесполезное"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscription_manager.subscribe(user_id)
    await update.message.reply_text("✅ Вы успешно подписались на уведомления!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscription_manager.unsubscribe(user_id)
    await update.message.reply_text("❌ Вы успешно отписались от уведомлений.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    is_subscribed = subscription_manager.is_subscribed(user_id)
    status_text = "🟢 Подписаны на уведомления" if is_subscribed else "🔴 Не подписаны"
    monitored_sites = monitor.get_monitored_sites()
    sites_text = "\n".join([f"• {site}" for site in monitored_sites]) if monitored_sites else "Нет активного мониторинга."
    await update.message.reply_text(f"{status_text}\n\nМониторинг сайтов:\n{sites_text}")

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("❌ Укажите URL для мониторинга.\nПример: /monitor https://example.com")
        return

    # Проверяем, что URL начинается с http:// или https://
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    monitor.add_site(url)
    await update.message.reply_text(f"🌐 Начинаю мониторинг сайта: {url}\nПервая проверка выполняется...")

    # Выполняем первую проверку для инициализации
    changes = monitor.check_changes(url)
    if changes.get("error"):
        await update.message.reply_text(f"❌ Ошибка при проверке сайта: {changes['error']}")
    elif changes.get("initialized"):
        await update.message.reply_text("✅ Сайт добавлен в мониторинг. Изменения будут отслеживаться автоматически.")

async def like_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_preferences.update_preference(user_id, "like")
    adapt_notifications(user_id, "like")
    await update.message.reply_text("👍 Спасибо за обратную связь! Будем показывать больше таких уведомлений.")

async def dislike_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_preferences.update_preference(user_id, "dislike")
    adapt_notifications(user_id, "dislike")
    await update.message.reply_text("👎 Спасибо за обратную связь! Постараемся улучшить качество уведомлений.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text.lower()
    user_id = update.effective_user.id

    if "like" in message:
        user_preferences.update_preference(user_id, "like")
        await update.message.reply_text("👍 Спасибо за лайк!")
    elif "dislike" in message:
        user_preferences.update_preference(user_id, "dislike")
        await update.message.reply_text("👎 Спасибо за отзыв!")

async def check_all_sites(application: Application) -> None:
    """Периодическая проверка всех сайтов на изменения"""
    monitored_sites = monitor.get_monitored_sites()
    if not monitored_sites:
        return

    subscribers = subscription_manager.get_subscribers()
    if not subscribers:
        return

    for url in monitored_sites:
        try:
            changes = monitor.check_changes(url)
            
            if changes.get("error"):
                logger.warning(f"Ошибка при проверке {url}: {changes['error']}")
                continue

            if changes.get("changed"):
                logger.info(f"Обнаружены изменения на {url}")
                # Отправляем уведомления всем подписчикам
                for subscriber_id in subscribers:
                    try:
                        analysis = analyze_changes_for_user(subscriber_id, changes)
                        await application.bot.send_message(
                            chat_id=subscriber_id,
                            text=f"🔔 Изменения на сайте {url}\n\n{analysis}"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления пользователю {subscriber_id}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при проверке сайта {url}: {e}")

async def setup_periodic_monitoring(application: Application) -> None:
    """Настройка периодического мониторинга"""
    global scheduler
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_all_sites,
        trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
        args=[application],
        id="check_sites",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Периодический мониторинг настроен (интервал: {CHECK_INTERVAL_MINUTES} минут)")