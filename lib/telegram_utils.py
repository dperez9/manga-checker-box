import time
import asyncio
import lib.database_utils as dbu
import lib.manga_web_utils as mwu
import lib.json_utils as ju
import lib.logger_utils as lu
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.ext import ContextTypes

# Obtemos los loggers
bot_logger = lu.bot_logger
manga_logger = lu.manga_logger

# Private vars
__manga_checker_box_passwd = ju.get_sign_up_passwd()
__admin_id = ju.get_admin_id()
__time_to_wait_between_search = ju.get_config_var("time_to_wait_between_search") # Segundos
__update_manga_list_time = 0
__yes = "Yes" # Option message 
__no = "No" # Option message

# COMMADNS ==============================================================================
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    user_nick = dbu.select_user_nick(user_id)
    bot_logger.info(f"{user_nick} ID({user_id}) - /HELP - User request help message")

    msg = "Avaliable commands list:\n\n"\
        "/start - Starts the bot\n" \
        "/help - Shows you avaliable commands\n" \
        "/tracking - Add a new series to your tracking list\n" \
        "/tracking_list - Show your tracking list\n" \
        "/untracking  - Remove a series of your tracking list\n"
        
    if str(user_id) == __admin_id:
        print("hola")
        msg = msg + \
        "\n------------------------------" \
        "\nAdmin commands list:\n" \
        "\n/notice - Allow to send a message to all users" \
        "\n/info - Allow to see how many users and manga are track\n" 

    msg = msg + "\nSelect or write one command"

    await update.message.reply_text(msg)

async def unrecognized_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_nick = dbu.select_user_nick(user_id)
    bot_logger.info(f"{user_nick} ID({user_id}) - /UNRECOGNIZED_COMMAMD - User sent an unrecognized message")
    await update.message.reply_text("Select or write /help to know what to do")

async def tracking_list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    user_nick = dbu.select_user_nick(user_id)
    bot_logger.info(f"{user_nick} ID({user_id}) - /TRACKING_LIST - User request tracking list")

    manga_table = dbu.select_user_manga_list(user_id)
    msg = __generate_tracking_list(manga_table)
    bot_logger.info(f"{user_nick} ID({user_id}) - /TRACKING_LIST - Sending tracking list")
    await update.message.reply_text(msg)

# JOB QUEAU ==============================================================================
# TRACKING_ALL ---------------------------------------------------------------------------
async def update_tracking(context: ContextTypes.DEFAULT_TYPE):
    notify = True 

    # Calculamos el tiempo que se tarda en actualizar todos los mangas
    init_time = time.time()
    await tracking_all(context, notify)
    end_time = time.time()

    __update_manga_list_time = end_time - init_time # Guardamos el tiempo en segundos
    minutes, seconds = divmod(__update_manga_list_time, 60)
    bot_logger.info(f"/TRACKING_ALL - It took {minutes:.0f}:{seconds:.0f} (min:sec)")
    

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
        already_registered_msg = f"{nick}, you are already registered. To see other options select or write /help"
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
    bot_logger.info(f"/SING_UP - Asking to User ID({user_id}) for nickname confirmation")
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
    advise_msg = advise_msg + "\nIntroduce a URL to track from one of this pages. It can take a few seconds to analyze the web site"
    await update.message.reply_text(advise_msg, parse_mode='Markdown')

    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - Waiting for URL to track")

    return TRACKING_CHECK_URL

async def tracking_check_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_input = update.message.text
    context.user_data['url'] = user_input
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - URL introduced: {user_input}")
    
    # Comprobamos si la URL es valida
    error_msg = "The introduced URL is not valid. Select /tracking to introduce a valid URL. Other wise select or write /help to get avaliable commands"
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
        
        registration_completed_msg = f"Perfect {context.user_data['nickname']}, {manga_name} last chapter is {last_chapter.strip()}. I will let you know with new chapters :P\nTo add a new series select /tracking. Other wise select or write /help to get avaliable commands"
        await update.message.reply_text(registration_completed_msg)

        return ConversationHandler.END
    
    # Se ser un nick incorrecto, volveremos a solicitarle un nick
    elif user_input == __no:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /TRACKING - The user didn't save the series")
        dont_save_msg = "The series wasn't save. Select or write /tracking to introduce a the tracking. Other wise select or write /help to get avaliable commands"
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

# UNTRACKING HANDLER ------------------------------------------------------------------------
UNTRACKING_ASK_CONFIRMATION, UNTRACKING_CONFIRMATION = range(2) # Le asingamos un numero a cada estado

async def untracking_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id
    context.user_data["nickname"] = dbu.select_user_nick(user_id)

    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Started untracking process")
    manga_table = dbu.select_user_manga_list(user_id)
    context.user_data["manga_table"] = manga_table

    if len(manga_table) == 0:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User is not tracking any series")
        await update.message.reply_text(f"You are not tracking any series. Select or write /help to get avaliable commands")
        context.user_data["manga_table"] = None
        return ConversationHandler.END
    
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Generating untracking list message")
    untracking_list_msg = __generate_untracking_list_msg(manga_table)
    await update.message.reply_text(untracking_list_msg)

    return UNTRACKING_ASK_CONFIRMATION

async def untracking_ask_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id
    user_input = update.message.text
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User sent: {user_input}")
    
    # Comprobamos si quiere cancelar el proceso
    if user_input == "/cancel":
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User abort the untracking process")
        await update.message.reply_text(f"Aborted untracking process. Select or write /help to get avaliable commands")
        context.user_data["manga_table"] = None
        return ConversationHandler.END
    
    # Comprobamos que el numero enviado por el usuario es una respuesta valida. El usuario debe devolver algo como esto: '/1', '/4', '/12' 
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Reading manga series number selection")
    selection_number = __get_untracking_selection_number(user_input)
    

    # Si no se ha detectado una seleccion terminamos
    if selection_number == None:
        await update.message.reply_text(f"I couldn't recognized a number selection. Aborted untracking process. To untrack a series select or write /untracking. Other wise select or write /help to get avaliable commands")
        context.user_data["manga_table"] = None
        return ConversationHandler.END
    
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - The number recognized was: '{selection_number+1}'")

    # Eliminamos el seguimiento del usuario
    manga_table = context.user_data["manga_table"]
    manga_del = manga_table[selection_number]
    context.user_data['manga_url'] = manga_del[0] # Obtenemos la URL en la posicion 0
    context.user_data['manga_name'] = manga_del[1] # Obtenemos la URL en la posicion 1
    context.user_data['manga_web'] = manga_del[3] # Obtenemos la URL en la posicion 3
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User selected: {context.user_data['manga_name']} - {context.user_data['manga_web']}")
    
    # Creamos las posibles respuestas a la pregunta
    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Asking for untracking confirmation")
    reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
    await update.message.reply_text(
        f"You want to remove '{context.user_data['manga_name']} - {context.user_data['manga_web']}' from your tracking list?", reply_markup=reply_markup
    )

    return UNTRACKING_CONFIRMATION

async def untracking_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_id = update.message.from_user.id
    manga_url = context.user_data['manga_url'] 
    manga_name = context.user_data['manga_name']
    manga_web = context.user_data['manga_web']

    bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User input was: {user_input}")

    if user_input == __yes:
        dbu.delete_tracking_row(user_id, manga_url)
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Removed tracking for {manga_name}")

        # Comprobamos que haya alguna mas gente siguiendo dicho manga, en caso contrario lo eliminamos de la tabla MANGA
        users_table = dbu.select_users_tracking_manga(manga_url)
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - The series '{manga_name} - {manga_web}' is follow by {len(users_table)} users")
        if len(users_table) == 0:
            bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - It is necesary remove it form MANGA table")
            dbu.delete_manga(manga_url)
            bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - The series '{manga_name} - {manga_web}' was removed form MANGA table")
        
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Sending final message")
        await update.message.reply_text(f"{manga_name} - {manga_web} was removed. To untracking another one, select or write /. Other wise select or write /help to get avaliable commands")    
        return ConversationHandler.END
        
    elif user_input == __no:
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - User canceled untracking process")
        await update.message.reply_text(f"The series '{manga_name} - {manga_web}' wasn't remove it. To remove another series select or write /untracking. Other wise select or write /help to get avaliable commands")
        return ConversationHandler.END
    
    else:
        # Creamos las posibles respuestas a la pregunta
        bot_logger.info(f"{context.user_data['nickname']} ID({user_id}) - /UNTRACKING - Asking for untracking confirmation")
        reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
        await update.message.reply_text(
            f"You want to remove '{context.user_data['manga_name']} - {context.user_data['manga_web']}' from your tracking list?", reply_markup=reply_markup
        )

        return UNTRACKING_CONFIRMATION
    

# NOTICE HANDLER ------------------------------------------------------------------------
NOTICE_ASK_CONFIRMATION, NOTICE_CONFIRMATION = range(2) # Le asingamos un numero a cada estado

async def notice_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = update.message.from_user.id

    # Si el escribe el comando no es admin finalizamos salimos del commando
    if str(user_id) != __admin_id:
        bot_logger.info(f"/NOTICE - A non user admin ID({user_id}) tried to send a notice")
        return ConversationHandler.END
    
    bot_logger.info(f"/NOTICE - Admin user wants to notice a message")

    msg = "Write a message to send to all Manga Checker Box users"
    await update.message.reply_text(msg)

    return NOTICE_ASK_CONFIRMATION

async def notice_ask_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Recibimos el mensaje
    user_input = update.message.text
    context.user_data['notice_msg'] = user_input
    bot_logger.info(f"/NOTICE - Admin sent the message:\n{user_input}")
    bot_logger.info(f"/NOTICE - Asking for confirmation")

    reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
    await update.message.reply_text(
        f"Are you sure you want to send this message?", reply_markup=reply_markup
    )

    return NOTICE_CONFIRMATION

async def notice_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_input = update.message.text
    bot_logger.info(f"/NOTICE - Admin input was: {user_input}")

    if user_input == __yes:
        bot_logger.info(f"/NOTICE - Admin accepted send the message")
        await notify_users_msg(context, context.user_data['notice_msg'])
        await update.message.reply_text(f"All messages where sent. Select or write /help to get avaliable commands")
        return ConversationHandler.END
    
    elif user_input == __no:
        bot_logger.info(f"/NOTICE - Admin discharged the message")
        await update.message.reply_text("The message was not send. Select or write /help to get avaliable commands")
        return ConversationHandler.END
    
    else:
        bot_logger.info(f"/NOTICE - Asking for confirmation again")

        reply_markup = ReplyKeyboardMarkup([[__yes, __no]], one_time_keyboard=True)
        await update.message.reply_text(
            f"Are you sure you want to send this message?", reply_markup=reply_markup
        )
        return NOTICE_CONFIRMATION

# METHODS ================================================================================

async def tracking_all(context: ContextTypes.DEFAULT_TYPE, notify: bool):
    
    bot_logger.info(f"/TRACKING_ALL - Starting tracking all")

    table = dbu.select_all_manga_table()
    total_manga = len(table)

    # Recorrer los registros y obtener los valores
    i = 1
    for row in table:
        url = row[0]
        name = row[1]
        last_chapter = row[2]
        web_name = row[3]
        bot_logger.info(f"/TRACKING_ALL - Tracking({i}/{total_manga}): {name} - {web_name}")
        await tracking(context, web_name, url, name, last_chapter, notify)
        await asyncio.sleep(__time_to_wait_between_search)
        i = i+1
    
    #bot_logger.info(f"/TRACKING_ALL - Tracked {total_manga} series")

async def tracking(context: ContextTypes.DEFAULT_TYPE, web_name: str , url: str, name: str, last_chapter: str, notify: bool):
    # Si ocurre algun error mostrar el mensaje y pasamos al siguiente
    try:
        new_chapters = mwu.check_manga(web_name, url, last_chapter)
        if len(new_chapters) > 0:
            if notify:
                manga_logger.info(__generate_message(name, new_chapters))
                await notify_users_manga(context, url, name, new_chapters)
            return True
    except Exception as error:
        bot_logger.warning(f"/TRACKING_ALL - Error while Tracking {name} - {web_name} - {url}\nError message: {error}")    
        print(f"{error}")
    
    return False

async def notify_users_manga(context: ContextTypes.DEFAULT_TYPE, manga_url: str, name: str, new_chapters: dict):
    
    bot_logger.info(f"/TRACKING_ALL - Notifying users about {name} new chapters")
    table = dbu.select_users_tracking_manga(manga_url)

    # Generamos un mensaje y notificamos a todos los users que sigan dicho link
    for row in table:
        user_id = row[0]
        msg = __generate_message(name, new_chapters)

        bot_logger.info(f"/TRACKING_ALL - User ID({user_id}) recieved a notification: {msg}")
        await context.bot.send_message(chat_id=user_id, text=msg)

async def notify_users_msg(context: ContextTypes.DEFAULT_TYPE, msg: str):
    
    bot_logger.info(f"/NOTICE - Notifying message to all users")
    table = dbu.select_all_users_table()

    # Enviamos el mensaje a todos los usuarios
    for row in table:
        user_id = row[0]
        user_nick = row[1]

        bot_logger.info(f"/NOTICE - Notifying {user_nick} ID({user_id})")
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

def __generate_tracking_list(manga_table: list):

    output = "Your tracking list:\n\n"
    for row in manga_table:
        name = row[1]
        web_name = row[3]
        output = output + f" > {name} - {web_name}\n"

    output = output + "\nSelect or write /help to get the command list"
    return output
    
def __generate_untracking_list_msg(manga_table: list):
    
    output = "Select a series to untrack (press the number attach to the series):\n\n"
    i = 0
    for row in manga_table:
        name = row[1]
        web_name = row[3]
        output = output + f"/{i+1} > {name} - {web_name}\n"
        i = i+1 

    output = output + f"\nPress /cancel to abort the operation"
    return output

def __get_untracking_selection_number(selection: str):

    output = None
    # Verifica si el texto comienza con '/'
    if selection.startswith('/'):
        # Extrae la parte numérica
        text_number = selection[1:]

        try:
            # Intentamos convertir el numero en un int
            number = int(text_number)-1
            output = number
        except ValueError:
            # En caso de que no se pueda convertir devolvemos None
            pass
    return output