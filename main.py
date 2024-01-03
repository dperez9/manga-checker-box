import lib.telegram_utils as tu
import lib.json_utils as ju
import lib.time_utils as timu
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

TOKEN = ju.get_api_token()
update_tracking_time_to_wait = ju.get_config_var("update_tracking_time_to_wait") # Tiempo en segundos
initial_tracking_time_wait = timu.seconds_until_next_hour()

# SIGN_UP_PASSWD HANDLER
sign_up_handler_passwd = ConversationHandler(
    entry_points=[CommandHandler("start", tu.sing_up_start_passwd)],
    states={
        tu.CHECK_PASSWD: [MessageHandler(filters.TEXT, tu.check_passwd)],
        tu.RECIEVE_NICK: [MessageHandler(filters.TEXT, tu.recieve_nick)],
        tu.NICK_CONFIRMATION: [MessageHandler(filters.TEXT, tu.nick_confirmation)]
    }, 
    fallbacks=[tu.error]
)

# SIGN_UP HANDLER
sign_up_handler = ConversationHandler(
    entry_points=[CommandHandler("start", tu.sing_up_start)],
    states={
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

# UNTRACKING HANDLER
untracking_handler = ConversationHandler(
    entry_points=[CommandHandler("untracking", tu.untracking_start)],
    states={
        tu.UNTRACKING_ASK_CONFIRMATION: [MessageHandler(filters.TEXT, tu.untracking_ask_confirmation)],
        tu.UNTRACKING_CONFIRMATION: [MessageHandler(filters.TEXT, tu.untracking_confirmation)]
    }, 
    fallbacks=[tu.error]
)

# MULTIPLE TRACKING HANDLER
multi_tracking_handler = ConversationHandler(
    entry_points=[CommandHandler("multi_tracking", tu.multi_tracking_start)],
    states={
        tu.MULTI_TRACKING_CHECK_URLS: [MessageHandler(filters.TEXT, tu.multi_tracking_check_urls)],
        tu.MULTI_TRACKING_CONFIRMATION: [MessageHandler(filters.TEXT, tu.multi_tracking_confirmation)]
    }, 
    fallbacks=[tu.error]
)

# END HANDLER
end_handler = ConversationHandler(
    entry_points=[CommandHandler("end", tu.end_start)],
    states={
        tu.END_CONFIRMATION: [MessageHandler(filters.TEXT, tu.end_confirmation)]
    }, 
    fallbacks=[tu.error]
)

# NOTICE HANDLER
notice_handler = ConversationHandler(
    entry_points=[CommandHandler("notice", tu.notice_start)],
    states={
        tu.NOTICE_ASK_CONFIRMATION: [MessageHandler(filters.TEXT, tu.notice_ask_confirmation)],
        tu.NOTICE_CONFIRMATION: [MessageHandler(filters.TEXT, tu.notice_confirmation)]
    }, 
    fallbacks=[tu.error]
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    # Simple Commands
    help_handler = CommandHandler('help', tu.help)
    info_handler = CommandHandler('info', tu.info)
    manga_updates_handler = CommandHandler('manga_updates', tu.manga_updates)
    update_tracking_handler = CommandHandler('update_tracking', tu.update_tracking_admin)
    tracking_list_handler = CommandHandler('tracking_list', tu.tracking_list)

    # Complex Commands - CommandHandlers
    application.add_handler(sign_up_handler)
    #application.add_handler(sign_up_handler_passwd)
    application.add_handler(help_handler)
    application.add_handler(tracking_handler)
    application.add_handler(multi_tracking_handler)
    application.add_handler(tracking_list_handler)
    application.add_handler(untracking_handler)
    application.add_handler(end_handler)
    application.add_handler(notice_handler)
    application.add_handler(info_handler)
    application.add_handler(manga_updates_handler)
    application.add_handler(update_tracking_handler)

    # Reply to no Commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tu.unrecognized_command))

    # Jobs
    application.job_queue.run_repeating(tu.update_tracking, interval=update_tracking_time_to_wait, first=initial_tracking_time_wait)
    #application.job_queue.run_repeating(tu.update_tracking, interval=update_tracking_time_to_wait, first=5)
    application.run_polling()

    