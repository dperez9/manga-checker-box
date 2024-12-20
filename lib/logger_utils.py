import os
import logging
from logging.handlers import TimedRotatingFileHandler
import lib.json_utils as ju

def create_path_and_file(file_path):
    """
    Crea todos los directorios necesarios para la ruta especificada y un archivo vacío al final.
    
    :param file_path: Ruta completa del archivo a crear.
    """
    # Extraer el directorio base de la ruta
    dir_path = os.path.dirname(file_path)
    
    # Crear los directorios si no existen
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Dirs already created: {dir_path}")
    
    # Crear el archivo vacío
    with open(file_path, 'w') as f:
        pass  # Solo crear el archivo, sin escribir contenido
    print(f"Log file created: {file_path}")


__logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
__suffix = '%Y-%m-%d.log'

# Configuración para el logger del bot
__bot_logs_path = ju.get_config_var("logs_path") + "bot/bot.log" 
create_path_and_file(__bot_logs_path)
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
create_path_and_file(__manga_logs_path)
__manga_change_file_handler = TimedRotatingFileHandler(__manga_logs_path, when="midnight", backupCount=30)
__manga_change_file_handler.suffix = __suffix 

__manga_formatter = logging.Formatter(__logger_format)
__manga_change_file_handler.setFormatter(__manga_formatter)

manga_logger = logging.getLogger('manga_logger')
manga_logger.addHandler(__manga_change_file_handler)


def get_manga_update_logs():
    lines = []
    with open(__manga_logs_path, 'r') as file:
        lines = file.readlines()
    return lines

def parse_log_entry(log_entry):
    # Dividir la cadena por los marcadores conocidos
    date, rest = log_entry.split(' ', 1)
    time, rest = rest.split(',', 1)
    _ = rest.split(' - ', 1)
    _ = rest.split('[NEW] ')[1]  # Descartar parte antes de [NEW]
    manga_name, rest = _.split(' - ', 1)
    chapter, rest = rest.split(' | Link: ', 1)
    link = rest.strip()

    return date, time, manga_name, chapter, link

