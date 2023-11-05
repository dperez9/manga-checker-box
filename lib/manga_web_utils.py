import os
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
import lib.database_utils as dbu 
import lib.json_utils as ju
# VARs ===========================================================================================
database_path = ju.get_config_var("database_path")
request_waiting_error_time = ju.get_config_var("request_waiting_error_time")
headers = ju.get_config_var("headers")

# METHODs ========================================================================================

def check_manga(web_name, url, last_chapter):
    
    # Buscamos que pagina web coincide
    if web_name == "Bato.to":
        return check_in_batoto(web_name, url, last_chapter)
    
    if web_name == "TuMangaOnline":
        return check_in_visortmo(web_name, url, last_chapter)
    
    if web_name == "Mangakakalot":    
        return check_in_mangakakalot(web_name, url, last_chapter)
    
    if web_name == "Mangakakalot.tv":    
        return check_in_mangakakalot_tv(web_name, url, last_chapter)

def check_manga_name(url: str):
    
    web_name = check_url(url)

    # Buscamos que pagina web coincide
    if web_name == "Bato.to":
        return check_batoto_url(url)
    
    if web_name == "TuMangaOnline":
        return check_visortmo_url(url)
    
    if web_name == "Mangakakalot":    
        return check_mangakakalot_url(url)
    
    if web_name == "Mangakakalot.tv":    
        return check_mangakakalot_tv_url(url)

# BATO.TO
def check_batoto_url(url: str):
    # Importamos la pagina en local
    # content=__load_local_web(url)

    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar el titulo del manga
    div_main = soup.find("div", class_="mainer")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'main'.")
    
    manga_title = div_main.find("a").text.strip()

    # Verifica si se encontró el titulo del manga
    if not manga_title:
        raise Exception("No se encontró el titulo del manga")
    
    return manga_title


def check_in_batoto(web_name:str, url: str, last_chapter: str) -> dict:
    """
    """
    # Importamos la pagina en local
    # local_web = url
    # content=__load_local_web(local_web)
    
    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    # print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar la lista de capítulos
    div_main = soup.find("div", class_="main")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'main'.")

    # Encuentra todos los enlaces (etiqueta <a>) dentro del div "main". Nos fijamos en la clase: "visited chapt"
    chapter_links = div_main.find_all("a", class_="visited chapt")

    # Buscamos cuantos capitulos nuevos hay
    batoto_url = __get_url_domain_db(web_name)
    new_chapters = __batoto_search_new_chapters(chapter_links, last_chapter, batoto_url)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)
    
    return new_chapters

def __batoto_search_new_chapters(chapters_list, last_chapter, batoto_url):
    new_chapters = {}
    for chapter_entry in chapters_list:
        # Nos tenemos que fijar en la etiqueta b
        chapter_number = chapter_entry.find("b").text

        # Si encontramos el ultimo capitulo leido hemos terminado
        if last_chapter == chapter_number: 
            break

        # Aniadimos el nombre del nuevo capitulo y su enlace
        chapter_id = chapter_entry['href']
        chapter_id = chapter_id[1:] # Eliminamos el primer caracter del id, que corresponde a la '/'
        new_chapters[chapter_number] = batoto_url+chapter_id
    
    return new_chapters

# TUMANGAONLINE
def check_visortmo_url(url: str):
    # Importamos la pagina en local
    # content=__load_local_web(url)

    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar el titulo del manga
    div_main = soup.find("div", class_="col-12 col-md-9 element-header-content-text")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'col-12 col-md-9 element-header-content-text'.")
    
    manga_title = div_main.find("h1", class_="element-title my-2").next_element.text.strip() # El metodo strip elimina los caracteres del tipo \n

    # Verifica si se encontró el titulo del manga
    if not manga_title:
        raise Exception("No se encontró el titulo del manga")
    
    return manga_title

def check_in_visortmo(web_name: str, url: str, last_chapter: str) -> str:
    """
    """
    # Importamos la pagina en local
    #local_web = url
    #content=__load_local_web(local_web)
    
    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    # print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar la lista de capítulos
    div_main = soup.find("div", class_="card chapters")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'main'.")

    # Encuentra todos los enlaces (etiqueta <a>) dentro del div "main". Nos fijamos en la clase: "visited chapt"
    chapter_links = div_main.find_all("a", class_="btn-collapse")

    # Buscamos cuantos capitulos nuevos hay
    new_chapters = __visortmo_search_new_chapters(chapter_links, last_chapter, url)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)
    
    return new_chapters

def __visortmo_search_new_chapters(chapters_list, last_chapter, lectortmo_url):
    '''
    '''
    new_chapters = {}
    for chapter_entry in chapters_list:
        # Nos tenemos que fijar en la etiqueta b
        chapter_number = chapter_entry.text[1:] # El primer caracter es un espacio, lo borramos

        # Si encontramos el ultimo capitulo leido hemos terminado
        if last_chapter == chapter_number: 
            break
        
        # Si cogemos 'href'del capitulo y hacemos un get a dicha dirección, la pagina nos muestra un mensaje de error
        # Por lo tanto, de enlace del capitulo guadamos la url de la lista
        new_chapters[chapter_number] = lectortmo_url
    
    return new_chapters

# MANGAKAKALOT
def check_mangakakalot_url(url: str):
    # Importamos la pagina en local
    # content=__load_local_web(url)

    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar el titulo del manga
    div_main = soup.find("div", class_="manga-info-top")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'col-12 col-md-9 element-header-content-text'.")
    
    manga_title = div_main.find("h1").text.strip() # El metodo strip elimina los caracteres del tipo \n

    # Verifica si se encontró el titulo del manga
    if not manga_title:
        raise Exception("No se encontró el titulo del manga")
    
    return manga_title


def check_in_mangakakalot(web_name: str, url: str, last_chapter: str) -> str:
    """
    """
    # Importamos la pagina en local
    # local_web = url
    # content=__load_local_web(local_web)
    
    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    # print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar la lista de capítulos
    div_main = soup.find("div", class_="chapter-list")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'main'.")

    # Encuentra todos los enlaces (etiqueta <a>) dentro del div "main". Nos fijamos en la clase: "visited chapt"
    chapter_links = div_main.find_all("a")

    # Buscamos cuantos capitulos nuevos hay
    new_chapters = __mangakakalot_search_new_chapters(chapter_links, last_chapter)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)

    return new_chapters

def __mangakakalot_search_new_chapters(chapters_list, last_chapter):
    '''
    '''
    new_chapters = {}
    for chapter_entry in chapters_list:
        # Nos tenemos que fijar en la etiqueta b
        chapter_number = chapter_entry.text # El primer caracter es un espacio, lo borramos

        # Si encontramos el ultimo capitulo leido hemos terminado
        if last_chapter == chapter_number: 
            break
        
        # Cogemos el enlace del capitulo
        link = chapter_entry['href']
        new_chapters[chapter_number] = link
    
    return new_chapters

# MANGAKAKALOT.TV
def check_mangakakalot_tv_url(url: str):
    # Importamos la pagina en local
    # content=__load_local_web(url)

    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar el titulo del manga
    div_main = soup.find("div", class_="manga-info-top")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'col-12 col-md-9 element-header-content-text'.")
    
    manga_title = div_main.find("h1").text.strip() # El metodo strip elimina los caracteres del tipo \n

    # Verifica si se encontró el titulo del manga
    if not manga_title:
        raise Exception("No se encontró el titulo del manga")
    
    return manga_title



def check_in_mangakakalot_tv(web_name: str, url: str, last_chapter: str) -> str:
    """
    """
    # Importamos la pagina en local
    #local_web = url
    #content=__load_local_web(local_web)
    
    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    # print("La petición fue aceptada")
    content = response.content
    
    # Analiza el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Encontrar la lista de capítulos
    div_main = soup.find("div", class_="chapter-list")

    # Verifica si se encontró el div principal
    if not div_main:
        raise Exception("No se encontró el div principal con id 'main'.")

    # Encuentra todos los enlaces (etiqueta <a>) dentro del div "main". Nos fijamos en la clase: "visited chapt"
    chapter_links = div_main.find_all("a")

    # Buscamos cuantos capitulos nuevos hay
    mangakakalot_url = __get_url_domain_db(web_name)
    new_chapters = __mangakakalot_tv_search_new_chapters(chapter_links, last_chapter, mangakakalot_url)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)

    return new_chapters

def __mangakakalot_tv_search_new_chapters(chapters_list, last_chapter, mangakakalot_url):
    '''
    '''
    new_chapters = {}
    for chapter_entry in chapters_list:
        # Nos tenemos que fijar en la etiqueta b
        chapter_number = chapter_entry.text # El primer caracter es un espacio, lo borramos

        # Si encontramos el ultimo capitulo leido hemos terminado
        if last_chapter == chapter_number: 
            break
        
        # Cogemos el enlace del capitulo
        chapter_id = chapter_entry['href']
        chapter_id = chapter_id[1:] # Quitamos el primer elemento del id que es la '/'
        new_chapters[chapter_number] = mangakakalot_url + chapter_id
    
    return new_chapters


# COMMON METHODs =================================================================================

def check_url(url:str) -> str:
    table = dbu.select_available_webs_url_check()
    for row in table:
        web_name = row[0]
        url_check = row[1]
        if url_check in url:
            return web_name
    return None

def __get_url_domain_db(domain: str):
    # Conectar a la base de datos
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Consulta para obtener la URL a partir del NAME
    query = 'SELECT URL FROM WEBS WHERE NAME = ?'
    cursor.execute(query, (domain,))
    result = cursor.fetchone()

    conn.close()
    return result[0]

def __load_local_web(local_web:str):
    # Obtener la ruta completa del archivo HTML
    path_html = os.path.join(os.getcwd(), local_web)

    # Verificar si el archivo HTML existe en la ruta
    if os.path.exists(path_html):
        # Leer el contenido del archivo HTML
        with open(path_html, 'r', encoding='utf-8') as file:
            html_content = file.read()

    return html_content

def __http_requests_to(url: str, attempts=3):
    
    answer = None
    for i in range(attempts):
        try:
            # Realizar la solicitud HTTP con requests.get()
            response = requests.get(url, headers=headers)
            
            # Comprobar si la solicitud fue exitosa (código de respuesta 200)
            if response.status_code == 200:
                answer = response
                break # Salimos del bucle
            else:
                raise Exception(f"[WARNING] It couldn't access to the web page({url}) - Attempt {i} - Status code: {response.status_code}")
        except Exception as error:
            # Mostrar un mensaje de advertencia
            print(f"{error}")
            # Esperar antes de intentar nuevamente
            time.sleep(request_waiting_error_time)
    
    return answer


        