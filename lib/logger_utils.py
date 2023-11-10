import logging
from logging.handlers import TimedRotatingFileHandler
import lib.json_utils as ju

__logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
__suffix = '%Y-%m-%d.log'

# Configuración para el logger del bot
__bot_logs_path = ju.get_config_var("logs_path") + "bot/bot.log" 
__bot_change_file_handler = TimedRotatingFileHandler(__bot_logs_path, when="midnight", backupCount=30) # Nos permitara ir actualizando el fichero log dia tras dia
__bot_change_file_handler.suffix = __suffix # Establecemos el nombre que tendra el fichero

__bot_formatter = logging.Formatter(__logger_format) # Creamos el formato de los logs
__bot_change_file_handler.setFormatter(__bot_formatter) # Le pasamos el formato el rotatingFileHandler

# Creamos el bot_logger
bot_logger = logging.getLogger() # Creamos el bot con e nombre del paquete (__name__)
bot_logger.setLevel(logging.INFO) # Le establecemos el nivel minimo de informacion
bot_logger.addHandler(__bot_change_file_handler) # Le pasamos el file handler
__console_logger = logging.StreamHandler() # Creamos un handler que nos permita visualizar los logs tambien por consola
__console_logger.setFormatter(__bot_formatter) # Le aplicamos el formato de los logs
bot_logger.addHandler(__console_logger)  # Establecemos que la informacion tambien se muestre en la consola

# Configuración para el logger de manga
__manga_logs_path = ju.get_config_var("logs_path") + "manga_updates/manga.log"
__manga_change_file_handler = TimedRotatingFileHandler(__manga_logs_path, when="midnight", backupCount=30)
__manga_change_file_handler.suffix = __suffix 

__manga_formatter = logging.Formatter(__logger_format)
__manga_change_file_handler.setFormatter(__manga_formatter)

manga_logger = logging.getLogger('manga_logger')
manga_logger.addHandler(__manga_change_file_handler)
