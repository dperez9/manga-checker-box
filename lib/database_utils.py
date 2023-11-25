import sqlite3
import lib.json_utils as ju

database_path = ju.get_config_var("database_path")

# INSERT METHODs =================================================================================

def insert_user(user_id: str, nick: str):
    # Conexion con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para insertar el valor en la tabla USERS
    query = 'INSERT INTO USERS (ID, NICK) VALUES (?, ?)'
    cursor.execute(query, (user_id, nick))

    # Confirmar los cambios
    conn.commit()
    conn.close()

def insert_manga(url, name, last_chapter, web_name):

    # Conectar a la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para insertar un nuevo manga en la tabla MANGA
    query = 'INSERT INTO MANGA (URL, NAME, LAST_CHAPTER, WEB_NAME) VALUES (?, ?, ?, ?)'
    cursor.execute(query, (url, name, last_chapter, web_name)) # Le pasamos una tupla con los tres valores

    # Confirmar los cambios en la base de datos
    conn.commit()
    conn.close()

def insert_tracking(user_id, manga_url):
    # Conectar a la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para insertar un nuevo seguimiento en la tabla TRACKING
    query = 'INSERT INTO TRACKING (USER_ID, MANGA_URL) VALUES (?, ?)'
    cursor.execute(query, (user_id, manga_url,))

    # Confirmar los cambios en la base de datos
    conn.commit()
    conn.close()

# SELECT METHODs =================================================================================

def select_user_nick(user_id: int) -> str:
    # Conexion con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla MANGA
    query = 'SELECT NICK FROM USERS WHERE ID = ?'
    cursor.execute(query, (user_id,))

    nick = cursor.fetchall()[0][0] # Primero selecionamos el primer valor de la tabla, y luego el primer valor de la tupla
    conn.close()

    return nick

def select_manga(url: str):
    # Conexion con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla MANGA
    query = 'SELECT NAME, LAST_CHAPTER, WEB_NAME FROM MANGA WHERE URL = ?'
    cursor.execute(query,(url,))

    table = cursor.fetchall()
    conn.close()

    return table

def select_all_users_table():
    # Conexion con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla MANGA
    query = 'SELECT ID, NICK FROM USERS'
    cursor.execute(query)

    table = cursor.fetchall()
    conn.close()

    return table

def select_all_manga_table():
    # Conexion con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla MANGA
    query = 'SELECT URL, NAME, LAST_CHAPTER,  WEB_NAME FROM MANGA'
    cursor.execute(query)

    table = cursor.fetchall()
    conn.close()

    return table

def select_users_tracking_manga(manga_url: str):
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'SELECT USER_ID FROM TRACKING WHERE MANGA_URL = ?'
    cursor.execute(query, (manga_url,))

    table = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    return table

def select_user_manga_list(user_id: str):
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = '''
        SELECT MANGA.*
        FROM TRACKING
        JOIN MANGA ON TRACKING.MANGA_URL = MANGA.URL
        WHERE TRACKING.USER_ID = ?
    '''
    cursor.execute(query, (user_id,))

    table = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    return table


def select_available_webs():
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'SELECT * FROM WEBS'
    cursor.execute(query)

    table = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    return table

def select_available_webs_url_check():
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'SELECT NAME, URL_CHECK FROM WEBS'
    cursor.execute(query)

    table = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    return table

def select_web_name_from_manga_url(url: str):
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'SELECT * FROM WEBS'
    cursor.execute(query)

    table = cursor.fetchall()
    conn.close()
    
    for row in table:
        name = row[0]
        web_url = row[1]

        if web_url in url:
            return name

    return ""
    
def select_users_tracking_manga(manga_url: str):
    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = '''
        SELECT USERS.*
        FROM USERS
        JOIN TRACKING ON USERS.ID = TRACKING.USER_ID
        WHERE TRACKING.MANGA_URL = ?
        '''
    cursor.execute(query, (manga_url,))

    table = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    return table

# UPDATE METHODs =================================================================================

def update_last_chapter(url: str, last_chapters: dict):
    last_chapter = list(last_chapters.keys())[0] # Obtenemos el ultimo capitulo

    # Conectamos a la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para actualizar el campo LAST_CHAPTER
    query = 'UPDATE MANGA SET LAST_CHAPTER = ? WHERE URL = ?'
    cursor.execute(query, (last_chapter, url))

    # Confirmar los cambios
    conn.commit()
    conn.close()

# CHECKS METHODs =================================================================================

def check_user_id(user_id: str):
    output = False
    # Conectando con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla WEBS
    query = "SELECT NICK FROM USERS WHERE ID = ?"
    cursor.execute(query, (user_id,))

    # Obtener todos los registros
    table = cursor.fetchall()
    conn.close()

    if len(table) > 0:
        output = True
        
    return output 
    
def check_manga_url(url:str):

    output = False

    # Conectando con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla WEBS
    query = 'SELECT NAME FROM MANGA WHERE URL = ?'
    cursor.execute(query, (url,))

    # Obtener todos los registros
    table = cursor.fetchall()
    conn.close()

    if len(table) == 1:
        output = True    
    return output


def check_valid_url(url: str):
    # Conectando con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla WEBS
    query = 'SELECT * FROM WEBS'
    cursor.execute(query)

    # Obtener todos los registros
    table = cursor.fetchall()
    conn.close()

    for row in table:
        web_name = row[0]
        domain = row[1]
        if domain in url:
            return web_name
        
    return None

def check_already_tracking(user_id: str, url: str):
    # Conectando con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla WEBS
    query = 'SELECT MANGA_URL FROM TRACKING WHERE USER_ID = ?'
    cursor.execute(query, (user_id,))

    # Obtener todos los registros
    table = cursor.fetchall()
    conn.close()

    for row in table:
        manga_url = row[0]
        if manga_url == url:
            return True
    return False

def check_is_javascript_web(web_name:str):
    # Conectando con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar todos los registros de la tabla WEBS
    query = 'SELECT JAVASCRIPT FROM WEBS WHERE NAME = ?'
    cursor.execute(query, (web_name,))

    # Obtener todos los registros
    table = cursor.fetchall()
    conn.close()

    if len(table) == 0:
        raise Exception(f"[ERROR] The web name '{web_name}' it doesn't exist")
    
    output = bool(table[0][0]) # Devuelve una lista de tuplas. En la primera tupla, se encuentra el valor
    return output


# DELETE METHODs =================================================================================
def delete_manga(manga_url: str):

    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'DELETE FROM MANGA WHERE URL = ?'
    cursor.execute(query, (manga_url,))

    table = cursor.fetchall()

    # Confirmar los cambios y cerrar la conexión con la base de datos
    conn.commit()
    conn.close()

def delete_tracking_row(user_id: str, manga_url: str):

    # Conectamos con la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para seleccionar USER_ID y NAME en función de MANGA_URL
    query = 'DELETE FROM TRACKING WHERE USER_ID = ? AND MANGA_URL = ?'
    cursor.execute(query, (user_id, manga_url))

    # Confirmar los cambios y cerrar la conexión con la base de datos
    conn.commit()
    conn.close()