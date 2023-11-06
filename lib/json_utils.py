import json

config_path = "json/config.json"

def read_json(path:str) -> dict: 
    """
    Lee un archivo JSON y devuelve su contenido como un diccionario.
    
    Args:
        path (str): La ruta al archivo JSON.

    Returns:
        dict: El contenido del archivo JSON como un diccionario.
    """
    # Intentamos abrir el json
    try:
        # Leemos el archivo
        with open(path, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print("The JSON file couldn't be finded in the especific path")
    except json.JSONDecodeError:
        print("Error reading JSON")

    return json_data

def save_json(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4) # Indent=4 para tener una identacion de 4 espacios en el archivo

def get_config_var(var: str) -> str:
    config_dict = read_json(config_path)
    output = config_dict[var]
    return output 

def get_api_token():
    key_path = get_config_var("token_path")
    output = ""
    with open(key_path, 'r') as file:
    # Lee la línea que desees, por ejemplo, la primera línea
        output = file.readline()

    return output

def get_sign_up_passwd():
    key_path = get_config_var("sing_up_passwd_path")
    output = ""
    with open(key_path, 'r') as file:
    # Lee la línea que desees, por ejemplo, la primera línea
        output = file.readline()

    return output 

def get_admin_id():
    key_path = get_config_var("admin_id")
    output = ""
    with open(key_path, 'r') as file:
    # Lee la línea que desees, por ejemplo, la primera línea
        output = file.readline()

    return output 