import sqlite3

# Script para hacer pruebas

def delete_all_users_except(database_path, user_id_to_keep):
    """
    Borra todos los usuarios y sus TRACKINGS, excepto el usuario especificado.

    :param database_path: Ruta al archivo de la base de datos SQLite.
    :param user_id_to_keep: ID del usuario que se desea conservar.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Identificar los TRACKINGS que deben ser eliminados
        cursor.execute("""
        DELETE FROM TRACKING
        WHERE USER_ID != ?;
        """, (user_id_to_keep,))

        # Borrar todos los usuarios excepto el especificado
        cursor.execute("""
        DELETE FROM USERS
        WHERE ID != ?;
        """, (user_id_to_keep,))

        # Eliminar MANGAS que no están siendo seguidos por el usuario especificado
        cursor.execute("""
        DELETE FROM MANGA
        WHERE URL NOT IN (
            SELECT MANGA_URL
            FROM TRACKING
            WHERE USER_ID = ?
        );
        """, (user_id_to_keep,))

        # Confirmar los cambios
        conn.commit()
        print(f"Se eliminaron todos los usuarios excepto el usuario con ID '{user_id_to_keep}'.")
    
    except sqlite3.Error as e:
        print(f"Error durante la eliminación: {e}")
        conn.rollback()
    
    finally:
        conn.close()

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de los parámetros
    NAME_DB = "./manga_tracker_dani.db"
    USER_ID_TO_KEEP = "495720289"  # Reemplaza con el ID real de tu usuario

    # Llamar a la función
    delete_all_users_except(NAME_DB, USER_ID_TO_KEEP)
