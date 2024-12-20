import sqlite3

def delete_manga_entry(database_path, manga_url):
    """
    Elimina todas las entradas de TRACKING para el MANGA_URL especificado y la 
    entrada correspondiente en MANGA.

    :param database_path: Ruta al archivo de la base de datos SQLite.
    :param manga_url: URL del manga que se debe eliminar.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Eliminar todas las entradas de la tabla TRACKING para el MANGA_URL especificado
        cursor.execute("""
        DELETE FROM TRACKING
        WHERE MANGA_URL = ?;
        """, (manga_url,))

        # Eliminar la entrada correspondiente en la tabla MANGA
        cursor.execute("""
        DELETE FROM MANGA
        WHERE URL = ?;
        """, (manga_url,))

        # Confirmar los cambios
        conn.commit()
        print(f"Se eliminaron todos los seguimientos del manga con URL '{manga_url}' y la entrada correspondiente en MANGA.")
    
    except sqlite3.Error as e:
        print(f"Error durante la eliminación: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    # Configuración de los parámetros
    NAME_DB = "./manga_tracker_dani.db"  # Ruta de la base de datos
    MANGA_URL = "https://zonatmo.com/library/manga/624/one-piece"  # URL del manga a eliminar

    # Llamar a la función
    delete_manga_entry(NAME_DB, MANGA_URL)
