import sqlite3

NAME_DB = "db/manga_tracker.db"

# Conecta con la base de datos y la crea si no existe
conn = sqlite3.connect(NAME_DB)

# Creamos un cursos para interacturar con la base de datos
cursor = conn.cursor()

# Creamos la tabla USERS, guardamos todos los usuarios que usan el servicio
query = (''' CREATE TABLE IF NOT EXISTS USERS
            (ID TEXT PRIMARY KEY,
            NICK TEXT NOT NULL);
         ''')

cursor.execute(query)

# Creamos la table WEBS, guardamos las webs disponibles en las que podemos buscar manga
query = (''' CREATE TABLE IF NOT EXISTS WEBS
            (NAME     TEXT PRIMARY KEY,
            URL       TEXT NOT NULL,
            URL_CHECK TEXT NOT NULL, 
            JAVASCRIPT NUMERIC NOT NULL);
         ''')

cursor.execute(query)

# Creamos la tabla MANGA, guardamos la URL que identifica cada manga y el último capitulo publicado
query = (''' CREATE TABLE IF NOT EXISTS MANGA
            (URL             TEXT PRIMARY KEY,
            NAME             TEXT NOT NULL,
            LAST_CHAPTER     TEXT,
            WEB_NAME         TEXT NOT NULL,
            FOREIGN KEY (WEB_NAME) REFERENCES WEBS(NAME) ON DELETE CASCADE);
         ''')

cursor.execute(query)

# Creamos la tabla TRACKING, guardamos los mangas que sigue cada usuario
query = (''' CREATE TABLE IF NOT EXISTS TRACKING
            (USER_ID    TEXT NOT NULL,
            MANGA_URL   TEXT NOT NULL,
            FOREIGN KEY (USER_ID) REFERENCES USERS(ID) ON DELETE CASCADE,
            FOREIGN KEY (MANGA_URL) REFERENCES MANGA(URL) ON DELETE CASCADE );
         ''')

cursor.execute(query)

# Guardamos los cambios y cerramos la conexion
conn.commit()

# Aniadimos las webs
# Ejecuta la consulta de inserción
query = "INSERT INTO WEBS (NAME, URL, URL_CHECK, JAVASCRIPT) VALUES (?, ?, ?, ?)"

# Manga Plus
web_name = "Manga Plus"
url = "https://mangaplus.shueisha.co.jp/"
url_check = "https://mangaplus.shueisha.co.jp/titles/"
javascript = 1
cursor.execute(query, (web_name, url, url_check, javascript))

# TuMangaOnline
web_name = "TuMangaOnline"
url = "https://visortmo.com/"
url_check = "https://visortmo.com/library/"
javascript = 0
cursor.execute(query, (web_name, url, url_check, javascript))

# Bato.to
web_name = "Bato.to"
url = "https://bato.to/"
url_check = "https://bato.to/series/"
javascript = 0
cursor.execute(query, (web_name, url, url_check, javascript))

# Mangakakalot
web_name = "Mangakakalot"
url = "https://mangakakalot.com/"
url_check = "https://mangakakalot.com/"
javascript = 0
cursor.execute(query, (web_name, url, url_check, javascript))

# Mangakakalot
web_name = "Mangakakalot.tv"
url = "https://ww7.mangakakalot.tv/"
url_check = "https://ww7.mangakakalot.tv/"
javascript = 0
cursor.execute(query, (web_name, url, url_check, javascript))

# MangaDex
web_name = "MangaDex"
url = "https://mangadex.org/"
url_check = "https://mangadex.org/title/"
javascript = 1
cursor.execute(query, (web_name, url, url_check, javascript))

# MangaSee
web_name = "MangaSee"
url = "https://mangasee123.com/"
url_check = "https://mangasee123.com/manga/"
javascript = 1
cursor.execute(query, (web_name, url, url_check, javascript))

# Dynasty Scans
web_name = "Dynasty Scans"
url = "https://dynasty-scans.com/"
url_check = "https://dynasty-scans.com/series/"
javascript = 0
cursor.execute(query, (web_name, url, url_check, javascript))

conn.commit()
conn.close()

