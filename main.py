import logging
import lib.telegram_utils as tu
import lib.json_utils as ju
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = ju.get_api_token()
update_tracking_time_to_wait = ju.get_config_var("update_tracking_time_to_wait") # Tiempo en segundos
logs_path = ju.get_config_var("logs_path")

# Configura el formato del log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(logs_path),
        logging.StreamHandler()
    ]
)

# SIGN_UP HANDLER
sign_up_handler = ConversationHandler(
    entry_points=[CommandHandler("start", tu.sing_up_start)],
    states={
        tu.CHECK_PASSWD: [MessageHandler(filters.TEXT, tu.check_passwd)],
        tu.RECIEVE_NICK: [MessageHandler(filters.TEXT, tu.recieve_nick)],
        tu.NICK_CONFIRMATION: [MessageHandler(filters.TEXT, tu.nick_confirmation)]
    }, 
    fallbacks=[tu.error]
)

# TRACKING HANDLER
tracking_handler = ConversationHandler(
    entry_points=[CommandHandler("tracking", tu.tracking_start)],
    states={
        tu.TRACKING_CHECK_URL: [MessageHandler(filters.TEXT, tu.tracking_check_url)],
        tu.TRACKING_CONFIRMATION: [MessageHandler(filters.TEXT, tu.tracking_confirmation)]
    }, 
    fallbacks=[tu.error]
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    # Commands
    help_handler = CommandHandler('help', tu.help)

    # CommandHandlers
    application.add_handler(help_handler)
    application.add_handler(sign_up_handler)
    application.add_handler(tracking_handler)

    # Jobs
    application.job_queue.run_repeating(tu.update_tracking, interval=update_tracking_time_to_wait, first=5)
    application.run_polling()

    