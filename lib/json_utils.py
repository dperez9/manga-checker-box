import json
from selenium import webdriver

config_path = "json/config.json"
record_path = "json/records.json"

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

def load_record(name: str):
    data = read_json(record_path)
    return data[name]

def save_record(name: str, var):
    data = read_json(record_path)
    data[name] = var
    save_json(record_path, data)

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

def load_webdriver()->webdriver:
    webdriver_browser = get_config_var("webdriver_browser")
    webdriver_browser_lower = webdriver_browser.lower()

    if webdriver_browser_lower == "chrome":
        driver = webdriver.Chrome()
    elif webdriver_browser_lower == "chromiumedge":
        driver = webdriver.ChromiumEdge()
    elif webdriver_browser_lower == "firefox":
        driver = webdriver.Firefox()
    elif webdriver_browser_lower == "edge":
        driver = webdriver.Edge()
    elif webdriver_browser_lower == "safari":
        driver = webdriver.Safari()
    else:
        print(f"[ERROR] Load_webdriver() - Error loading a valid web browser, {webdriver_browser} wasn't found. Loading Chrome instead. List of avaliable browsers: Chrome, ChromiumEdge, Firefox, Edge and Safari")
        driver = webdriver.Chrome()

    return driver