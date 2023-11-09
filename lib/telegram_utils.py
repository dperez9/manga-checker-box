import asyncio
import logging
import time
from logging.handlers import TimedRotatingFileHandler
import lib.database_utils as dbu
import lib.manga_web_utils as mwu
import lib.json_utils as ju
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
suffix = '%Y-%m-%d.log'

# Configuración para el logger del bot
bot_logs_path = ju.get_config_var("logs_path") + "bot/today.log" 
bot_change_file_handler = TimedRotatingFileHandler(bot_logs_path, when="midnight", backupCount=30) # Nos permitara ir actualizando el fichero log dia tras dia
bot_change_file_handler.suffix = suffix # Establecemos el nombre que tendra el fichero

bot_formatter = logging.Formatter(logger_format) # Creamos el formato de los logs
bot_change_file_handler.setFormatter(bot_formatter) # Le pasamos el formato el rotatingFileHandler

# Creamos el bot_logger
bot_logger = logging.getLogger('bot_logger') # Creamos el bot con e nombre especificado
bot_logger.setLevel(logging.INFO) # Le establecemos el nivel minimo de informacion
bot_logger.addHandler(bot_change_file_handler) # Le pasamos el file handler
bot_logger.addHandler(logging.StreamHandler())  # Establecemos que la informacion tambien se muestre en la consola

# Configuración para el logger de manga
manga_logs_path = ju.get_config_var("logs_path") + "manga_updates/today.log"
manga_change_file_handler = TimedRotatingFileHandler(manga_logs_path, when="midnight", backupCount=30)
manga_change_file_handler.suffix = suffix 

manga_formatter = logging.Formatter(logger_format)
manga_change_file_handler.setFormatter(manga_formatter)

manga_logger = logging.getLogger('manga_logger')
manga_logger.setLevel(logging.INFO)
manga_logger.addHandler(manga_change_file_handler)

# Private vars
__manga_checker_box_passwd = ju.get_sign_up_passwd()
__adming_id = ju.get_admin_id()
__time_to_wait_between_search = ju.get_config_var("time_to_wait_between_search") # Segundos
__yes = "Yes"
__no = "No"

# COMMADNS ==============================================================================
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Here you got the avaliable commands list:\n"\
        "/start - Starts the bot\n" \
        "/help - Shows you avaliable commands\n" \
        "/tracking - Add a new series to your tracking"
    
    await update.message.reply_text(msg)

# JOB QUEAU ==============================================================================
# TRACKING_ALL ---------------------------------------------------------------------------
async def update_tracking(context: ContextTypes.DEFAULT_TYPE):
    notify = True
    await tracking_all(context, notify)

# CONVERSATION HANDLER ===================================================================
# SING_UP HANDLER ------------------------------------------------------------------------
CHECK_PASSWD, RECIEVE_NICK, NICK_CONFIRMATION = range(3) # Le asingamos un numero a cada estado

# Definimos los nombres de los estados del login
async def sing_up_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id
    bot_logger.info(f"/SING_UP - Starting sign up for User ID({user_id})")

    # Comprobamos si el usuario ya esta registado
    bot_logger.info(f"/SING_UP - Checking User ID({user_id}) in database")
    if dbu.check_user_id(user_id) == True:
        nick = dbu.select_user_nick(user_id)
        bot_logger.info(f"/SING_UP - User {nick}({user_id}) found, aborting sign up")
        already_registered_msg = f"{nick}, you are already registered"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=already_registered_msg)

        return ConversationHandler.END
    
    bot_logger.info(f"/SING_UP - The User ID({user_id}) doesn't exists")

    # Comienza la conversacion y te pide la contrasenia
    bot_logger.info(f"/SING_UP - Asking to User ID({user_id}) for secret password")
    passwd_msg = "Enter the secret password to use the service"
    await update.message.reply_text(passwd_msg)

    return CHECK_PASSWD

async def check_passwd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id

    # Comprobamos si la contrasenia facilitada es correcta para continuar el resgistro
    user_input = update.message.text.lower()
    bot_logger.info(f"/SING_UP - The user ID({user_id}) send: {user_input}")
    
    # Si la contrasenia es incorrecta avisamos al usuario y terminamos
    if user_input != __manga_checker_box_passwd:
        bot_logger.info(f"/SING_UP - The user ID({user_id}) send a wrong password")
        wrong_password_msg = "Wrong password, canceled sign up. To try again write again the /start command"
        await update.message.reply_text(wrong_password_msg)

        return ConversationHandler.END
    else:
    # Si la contrasenia es correcta continuamos con el registro y le preguntamos su apodo
        bot_logger.info(f"/SING_UP - The user ID({user_id}) send the right password")
        bot_logger.info(f"/SING_UP - Asking to User ID({user_id}) for a nickname")
        await update.message.reply_text("What is your nickname?")

        return RECIEVE_NICK

async def recieve_nick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id
    context.user_data["nickname"] = update.message.text
    bot_logger.info(f"/SING_UP - User ID({user_id}) send the nickname: {context.user_data['nickname']}")
    
    # Creamos las posibles respuestas a la pregunta
    bot_logger.info(f"Asking to User ID({user_id}) for nickname confirmation")
    reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
    await update.message.reply_text(
        f"The nickname '{context.user_data['nickname']}' is right?", reply_markup=reply_markup
    )
    return NICK_CONFIRMATION


async def nick_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id

    # Ponemos todo en minusculas
    user_input = update.message.text
    bot_logger.info(f"/SING_UP - User ID({user_id}) anwser: {user_input}")

    # De ser un nick valido, registramos al usuario en la base de datos y terminamos
    if user_input == __yes:
        # Registramos al usuario en la base de datos
        nick = context.user_data['nickname']
        dbu.insert_user(user_id, nick)

        # Le enviamos un mensaje de confirmacion
        bot_logger.info(f"/SING_UP - Registration completed for {nick} ID({user_id})")
        registration_completed_msg = f"Perfect {context.user_data['nickname']}, registration completed!\nSelect /help to see avaliable commands"
        await update.message.reply_text(registration_completed_msg)

        return ConversationHandler.END
    
    # Se ser un nick incorrecto, volveremos a solicitarle un nick
    elif user_input == __no:
        bot_logger.info(f"/SING_UP - User ID({user_id}) wrote a wrong nickname")
        bot_logger.info(f"/SING_UP - Asking to User ID({user_id}) for a nickname")
        await update.message.reply_text("What is your nickname?")

        return RECIEVE_NICK

    # De ingresar un caracter diferente, volveremos a preguntarle si el nick es valido
    else:
        bot_logger.info(f"/SING_UP - User ID({user_id}) wrote a invalid answer")

        # Creamos las posibles respuestas a la pregunta
        bot_logger.info(f"/SING_UP - Asking to User ID({user_id}) for nickname confirmation")
        reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
        await update.message.reply_text(
            f"The nickname '{context.user_data['nickname']}' is right?", reply_markup=reply_markup
        )

        return NICK_CONFIRMATION

# TRACKING HANDLER ------------------------------------------------------------------------
TRACKING_CHECK_URL, TRACKING_CONFIRMATION = range(2) # Le asingamos un numero a cada estado

async def tracking_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id
    context.user_data["nickname"] = dbu.select_user_nick(user_id)
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Starting tracking process")

    # Le mostramos un mensaje el cual estipule que webs estan disponibles, despues
    # Le pedimos al usuario que nos facilite una URl a la cual hacerle seguimiento
    advise_msg = "This is the list of available web pages list:\n\n"
    advise_msg = advise_msg + __generate_available_webs_msg()
    advise_msg = advise_msg + "\nIntroduce a URL to track from one of this pages"
    await update.message.reply_text(advise_msg, parse_mode='Markdown')

    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Waiting for URL to track")

    return TRACKING_CHECK_URL

async def tracking_check_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_input = update.message.text
    context.user_data['url'] = user_input
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - URL introduced: {user_input}")
    
    # Comprobamos si la URL es valida
    error_msg = "The introduced URL is not valid. Select /tracking to introduce a valid URL"
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Checking URL")
    web_name = mwu.check_url(user_input)

    if web_name == None:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The introduced URL is not valid")
        await update.message.reply_text(error_msg)

        return ConversationHandler.END

    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The introduced URL is from {web_name}")

    if dbu.check_already_tracking(user_id, user_input):
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - {context.user_data['nickname']} is already tracking {user_input}")
        await update.message.reply_text(f"You are tracking this series already. To add a new series, select again the /tracking command")

        return ConversationHandler.END
    
    # Ahora buscamos el nombre del manga
    manga_name = None
    try:
        manga_name = mwu.check_manga_name(user_input)
    except Exception as error:
        manga_name = None
        bot_logger.warning(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - There was a problem resolving the name of the series in the URL")
    
    if manga_name == None:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The introduced URL is not valid, couldn't resolve the manga name")
        await update.message.reply_text(error_msg)

        return ConversationHandler.END

    # Lo guardamos en el contexto de la conversacion
    context.user_data['manga_name'] = manga_name
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The name of the series is: {context.user_data['manga_name']}")
    
    # Creamos las posibles respuestas a la pregunta
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Asking for track confirmation")
    reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
    await update.message.reply_text(
        f"You want to add '{context.user_data['manga_name']}' to your tracking list?", reply_markup=reply_markup
    )

    return TRACKING_CONFIRMATION

async def tracking_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id

    # Ponemos todo en minusculas
    user_input = update.message.text
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - User answer: {user_input}")

    # De ser un nick valido, registramos al usuario en la base de datos y terminamos
    if user_input == __yes:
        # Comprobamos si el manga se encuentra en la lista de mangas
        url = context.user_data['url']
        manga_name = context.user_data['manga_name']

        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Checking if manga is already in database")
        check = dbu.check_manga_url(url)

        if not check:
            bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - It not registered, creating an entry in database for {manga_name}")
            # Cremos una entrada en la base de datos para dicha serie
            web_name = dbu.select_web_name_from_manga_url(url)
            dbu.insert_manga(url, manga_name, "", web_name)
            bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Entry created")

            # Actualizamos el ultimo capitulo del manga
            bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Tracking {manga_name} and updating last chapter registered")
            notify = False
            await tracking(context, web_name, url, manga_name, "", notify)

        # Buscamos el capitulo actualizado en la base de datos
        table = dbu.select_manga(url)
        last_chapter = table[0][1] # Fila 0 de la tabla (la unica que hay), posicion 1
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - {manga_name} last chapter is {last_chapter.strip()}")

        # Introducimos en la tabla tracking la informacion
        dbu.insert_tracking(user_id, url)
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Added to Tracking table the track: {context.user_data['nickname']} - {manga_name}")

        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Sending final message to user")
        
        registration_completed_msg = f"Perfect {context.user_data['nickname']}, {manga_name} last chapter is {last_chapter.strip()}. I will let you know with new chapters :P\nTo add a new series selects /tracking"
        await update.message.reply_text(registration_completed_msg)

        return ConversationHandler.END
    
    # Se ser un nick incorrecto, volveremos a solicitarle un nick
    elif user_input == __no:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The user didn't save the series")
        dont_save_msg = "The series wasn't save. Select /tracking to introduce a the tracking"
        await update.message.reply_text(dont_save_msg)

        return ConversationHandler.END

    # De ingresar un caracter diferente, volveremos a preguntarle si el nick es valido
    else:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - User wrote a invalid answer")

        # Creamos las posibles respuestas a la pregunta
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Asking for track confirmation")
        reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
        await update.message.reply_text(
            f"You want to add '{context.user_data['manga_name']}' to your tracking list?", reply_markup=reply_markup
        )

        return TRACKING_CONFIRMATION

# NOTICE HANDLER ------------------------------------------------------------------------

async def notice_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id

    # Si el escribe el comando no es admin finalizamos salimos del commando
    if user_id != __adming_id:
        return None
    bot_logger.info(f"/NOTICE - Admin user wants to notice a message")

    msg = "Write a message to send to all Manga Checker Box users"
    await update.message.reply_text(msg)

    # Recibimos el mensaje
    user_input = update.message.text
    bot_logger.info(f"/NOTICE - Admin sent the message:\n{user_input}")
    bot_logger.info(f"/NOTICE - Asking for confirmation")

    reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
    await update.message.reply_text(
        f"Are you sure you want to send the message?", reply_markup=reply_markup
    )

    user_input = update.message.text
    bot_logger.info(f"/NOTICE - Admin input was: {user_input}")
    bot_logger.info(f"/NOTICE - Sending the message")
    await context.bot.send_message(chat_id=user_id, text=user_input)



# METHODS ================================================================================

async def tracking_all(context: ContextTypes.DEFAULT_TYPE, notify: bool):
    
    bot_logger.info(f"/TRACKING_ALL - Starting tracking all")

    table = dbu.select_all_manga_table()
    total_manga = len(table)

    # Recorrer los registros y obtener los valores
    for row in table:
        url = row[0]
        name = row[1]
        last_chapter = row[2]
        web_name = row[3]
        
        await tracking(context, web_name, url, name, last_chapter, notify)
        await asyncio.sleep(__time_to_wait_between_search)
    
    bot_logger.info(f"/TRACKING_ALL - Tracked {total_manga} series")

async def tracking(context: ContextTypes.DEFAULT_TYPE, web_name: str , url: str, name: str, last_chapter: str, notify: bool):
    # Si ocurre algun error mostrar el mensaje y pasamos al siguiente
    bot_logger.info(f"/TRACKING_ALL - Tracking: {name} - {web_name}")

    try:
        new_chapters = mwu.check_manga(web_name, url, last_chapter)
        if len(new_chapters) > 0:
            if notify:
                manga_logger.info(__generate_message(name, new_chapters))
                await notify_users(context, url, name, new_chapters)
            return True
    except Exception as error:
        bot_logger.warning(f"/TRACKING_ALL - Error while Tracking {name} - {web_name} - {url}\nError message: {error}")    
        print(f"{error}")
    
    return False

async def notify_users(context: ContextTypes.DEFAULT_TYPE, manga_url: str, name: str, new_chapters: dict):
    
    bot_logger.info(f"/TRACKING_ALL - Notifying users about {name} new chapters")
    table = dbu.select_users_tracking_manga(manga_url)

    # Generamos un mensaje y notificamos a todos los users que sigan dicho link
    for row in table:
        user_id = row[0]
        msg = __generate_message(name, new_chapters)

        bot_logger.info(f"/TRACKING_ALL - User ID({user_id}) recieved a notification: {msg}")
        await context.bot.send_message(chat_id=user_id, text=msg)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    bot_logger.info(f"User ID({user_id}) canceled the conversation")
    await update.message.reply_text(
        f"Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def __generate_message(name:str, chapters: dict) -> str: 

    if len(chapters) == 1:
        chapter_number = list(chapters.keys())[0]
        chapter_url = chapters[chapter_number]
        
        msg = f"[NEW] {name} - {chapter_number.strip()} | Link: {chapter_url}"
        return msg

    elif len(chapters) >= 2:
        chapter_number = list(chapters.keys())[-1] # Cogemos la ultima clave de la lista, para mostrar el primer capitulo no leido
        chapter_url = chapters[chapter_number]
        
        msg = f"[NEW] {name} - {len(chapters)} Chapters | Link: {chapter_url}"
        return msg
    
    else:
        return ""
    
def __generate_available_webs_msg():

    # Crearemos un mensaje que muestre el nombre de las webs y sus URLs
    msg = ""
    table = dbu.select_available_webs()
    
    for row in table:
        name = row[0]
        url = row[1]
        msg = msg + f"{name} - {url}\n"
    
    return msg
    