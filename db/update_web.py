import sqlite3

def update_web_and_urls(database_path, web_name, old_url, new_url, new_url_check):
    """
    Actualiza la información de una web y las URLs relacionadas en la base de datos.

    :param database_path: Ruta al archivo de la base de datos SQLite.
    :param web_name: Nombre de la web a actualizar.
    :param old_url: URL anterior de la web.
    :param new_url: Nueva URL de la web.
    :param new_url_check: Nueva URL_CHECK de la web.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Actualizar la tabla WEBS
        cursor.execute("""
        UPDATE WEBS
        SET URL = ?, 
            URL_CHECK = ?
        WHERE NAME = ?;
        """, (new_url, new_url_check, web_name))

        # Actualizar las URLs en la tabla MANGA
        cursor.execute("""
        UPDATE MANGA
        SET URL = REPLACE(URL, ?, ?)
        WHERE WEB_NAME = ?;
        """, (old_url, new_url, web_name))

        # Actualizar las URLs en la tabla TRACKING
        cursor.execute("""
        UPDATE TRACKING
        SET MANGA_URL = REPLACE(MANGA_URL, ?, ?)
        WHERE MANGA_URL LIKE ?;
        """, (old_url, new_url, f"{old_url}%"))

        # Confirmar los cambios
        conn.commit()
        print("Actualización completada con éxito.")
    
    except sqlite3.Error as e:
        print(f"Error durante la actualización: {e}")
        conn.rollback()
    
    finally:
        conn.close()

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de los parámetros
    NAME_DB = "./manga_tracker.db"
    WEB_NAME = "TuMangaOnline"
    OLD_URL = "https://visortmo.com/"
    NEW_URL = "https://zonatmo.com/"
    NEW_URL_CHECK = "https://zonatmo.com/library/"

    # Llamar a la función
    update_web_and_urls(NAME_DB, WEB_NAME, OLD_URL, NEW_URL, NEW_URL_CHECK)
