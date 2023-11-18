import os
import re
import time
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import lib.database_utils as dbu 
import lib.json_utils as ju

# VARs ===========================================================================================
database_path = ju.get_config_var("database_path")
request_waiting_error_time = ju.get_config_var("request_waiting_error_time")
headers = ju.get_config_var("headers")

# METHODs ========================================================================================

def check_manga_name(url: str):
    
    web_name = check_url(url)

    if web_name == None:
        raise Exception(f"The URl({url}) is not from a valid web site")

    # Buscamos que pagina web coincide
    if web_name == "Manga Plus":
        return check_mangaplus_url(url)
    
    if web_name == "Bato.to":
        return check_batoto_url(url)
    
    if web_name == "TuMangaOnline":
        return check_visortmo_url(url)
    
    if web_name == "Mangakakalot":    
        return check_mangakakalot_url(url)
    
    if web_name == "Mangakakalot.tv":    
        return check_mangakakalot_tv_url(url)
    
    if web_name == "MangaDex":    
        return check_mangadex_url(url)


def check_manga(web_name, url, last_chapter):
    
    # Buscamos que pagina web coincide
    if web_name == "Manga Plus":
        return check_in_mangaplus(web_name, url, last_chapter)
    
    if web_name == "Bato.to":
        return check_in_batoto(web_name, url, last_chapter)
    
    if web_name == "TuMangaOnline":
        return check_in_visortmo(web_name, url, last_chapter)
    
    if web_name == "Mangakakalot":    
        return check_in_mangakakalot(web_name, url, last_chapter)
    
    if web_name == "Mangakakalot.tv":    
        return check_in_mangakakalot_tv(web_name, url, last_chapter)

    if web_name == "MangaDex":    
        return check_in_mangadex(web_name, url, last_chapter)
    

# MANGA PLUS
def check_mangaplus_url(url: str):
    
    # Copnfiguramos el driver de Selenium
    driver = webdriver.Chrome()

    # Obtemos la pagina web
    try: 
        driver.get(url)
    except Exception as error:
        raise Exception(f"Error requesting the url({url})")

    # Definimos los elementos a buscar
    manga_name_class = "TitleDetailHeader-module_title_Iy33M"
    javascript_wait_time = 10 # Tiempo de espera maximo para cargar la pagina

    #Espera a que los elementos con la clase deseada estén presentes en la web
    manga_title = None
    try:
        title = WebDriverWait(driver, javascript_wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, manga_name_class))
        )
    except Exception as error:
        raise Exception(f"Error finding manga title({url})")

    # Guardamos el titulo
    manga_title = title.text.title() # title() Deja todas las palabras con la primera en mayuscula y el resto en minusculas

    # Cerramos el navegador
    driver.quit()

    return manga_title

def check_in_mangaplus(web_name:str, url: str, last_chapter: str):
    
    # Copnfiguramos el driver de Selenium
    driver = webdriver.Chrome()

    # Obtemos la pagina web
    driver.get(url)

    # Definimos los elementos a buscar
    chapter_list_class = "TitleDetail-module_main_19fsJ" # Clase que contiene la lista de mangas
    chapters_class_name = "ChapterListItem-module_title_3Id89" # Clase de los capitulos
    javascript_wait_time = 10 # Tiempo de espera maximo para cargar la pagina

    #Espera a que los elementos con la clase deseada estén presentes en la web
    WebDriverWait(driver, javascript_wait_time).until(
        EC.presence_of_element_located((By.CLASS_NAME, chapter_list_class))
    )

    # Hacemos scroll hacia abajo para que carguen todos los capitulos
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Esperar a que la página cargue después del desplazamiento
    time.sleep(0.8)

    # Obtiene el HTML de la página después de que se haya cargado completamente
    html = driver.page_source

    # Ahora puedes analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Encuentra todos los enlaces (etiqueta <p>) con la clase de los capitulos
    chapter_list = soup.find_all("p", class_=chapters_class_name)

    new_chapters = __mangaplus_search_new_chapters(chapter_list, last_chapter, url)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)
    
    return new_chapters

def __mangaplus_search_new_chapters(chapters_list, last_chapter, mangaplus_url):
    new_chapters = {}
    i = 0 # De forma general, se muestran los ultimos 3 capitulos y los 3 primeros. Despues de ver los 3 ultimos terminamos
    for chapter_entry in reversed(chapters_list):
        # Nos tenemos que fijar en la etiqueta b
        chapter_number = chapter_entry.text

        # Si encontramos el ultimo capitulo leido hemos terminado o si hemos consultado los 3 ultimos capitulos disponibles
        if (last_chapter == chapter_number) or (i == 3): 
            break

        # Aniadimos el nombre del nuevo capitulo y su enlace, en este caso el enlace del cap no aparece
        new_chapters[chapter_number] = mangaplus_url
        
        # Aumentamos el contador
        i = i + 1
    
    return new_chapters

# BATO.TO
def check_batoto_url(url: str):
    # Importamos la pagina en local
    # content=__load_local_web(url)

    # Realizamos la solicitud HTTP
    response = __http_requests_to(url)

    if response == None:
        raise Exception(f"Error getting access to the web page({url})")
    
    # print("La petición fue aceptada")
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

# MANGADEX
def check_mangadex_url(url: str):
    
    # Copnfiguramos el driver de Selenium
    driver = webdriver.Chrome()

    # Obtemos la pagina web
    try: 
        driver.get(url)
    except Exception as error:
        raise Exception(f"Error requesting the url({url})")

    # Definimos los elementos a buscar
    manga_name_class = "mb-1"
    javascript_wait_time = 10 # Tiempo de espera maximo para cargar la pagina

    #Espera a que los elementos con la clase deseada estén presentes en la web
    manga_title = None
    try:
        title = WebDriverWait(driver, javascript_wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, manga_name_class))
        )
    except Exception as error:
        raise Exception(f"Error finding manga title({url})")

    # Guardamos el titulo
    manga_title = title.text.title() # title() Deja todas las palabras con la primera en mayuscula y el resto en minusculas

    # Cerramos el navegador
    driver.quit()

    return manga_title

def check_in_mangadex(web_name:str, url: str, last_chapter: str):
    
    # Copnfiguramos el driver de Selenium
    driver = webdriver.Chrome()

    # Obtemos la pagina web
    driver.get(url)

    # Definimos los elementos a buscar
    chapter_list_class = "flex-grow" # Clase que contiene la lista de mangas
    javascript_wait_time = 10 # Tiempo de espera maximo para cargar la pagina

    #Espera a que los elementos con la clase deseada estén presentes en la web
    WebDriverWait(driver, javascript_wait_time).until(
        EC.presence_of_element_located((By.CLASS_NAME, chapter_list_class))
    )

    # Hacemos scroll hacia abajo para que carguen todos los capitulos
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Esperar a que la página cargue después del desplazamiento
    time.sleep(0.8)

    # Obtiene el HTML de la página después de que se haya cargado completamente
    html = driver.page_source

    # Ahora puedes analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Ahora debemos encontrar los enlaces, para ello buscaremos el titulo(Ejemplo): Chapter 156
    # Sin embargo, la pagina agrupa los capitulos de dos formas distintas.

    # Cuando se sube un primer capitulo, se guarda de una forma, con la etiqueta <a class="flex flex-grow items-center">
    # Pero cuando se han subido varias versiones del mismo capitulo los agrupa, poniendo el
    # numero del capitulo y luego varias entrada para cada fansub (conmunmente cada uno en un idioma).
    # Para ello utilizan la etiqueta <span class="font-bold self-center whitespace-nowrap">

    # Por lo tanto, primero tenemos que identificar los capitulos sueltos y despues seguir los agrupados.
    # Los capitulos sueltos cuando son agregados empiezan de la misma forma: 'Ch. '
    # Seguido del numero del capitulo, guion, y el titulo del cap. Cuando estan agrupados, solo ponen el titulo para cada
    # fansub y el numero del cap viene de cabecera

    # La estrategia sera buscar todos las etiquetas <a> que empiecen por 'Ch. ', para así poder obtener
    # El numero del capitulo, y despues continuar buscando los capitulos agrupados con <span>. De esta forma,
    # Buscaremos solo el numero del capitulo y no del titulo (porque puede estar en varios idiomas)

    # Se ha decidido por buscar primero el tipo <a>, y en caso de que no se encuentre buscamos por <span>
    chapter_a_name = "flex flex-grow items-center"
    chapters_span_name = "font-bold self-center whitespace-nowrap" # Clase de los capitulos

    # Buscamos por la etiqueta de tipo <a>
    a_list = soup.find_all("a", class_=chapter_a_name)
    chapter_list_a = __find_a_mangaplus_chapters(a_list)
    
    span_list = soup.find_all("span", class_=chapters_span_name)
    chapter_list_span = __find_span_mangaplus_chapters(span_list)

    chapter_list = chapter_list_a + chapter_list_span

    # Ordenamos los capitulos, porque pueden estar desordenados al combinar las listas
    # Función que extrae el número de la cadena
    extract_number = lambda chapter: float(chapter.split()[-1]) # Dividimos las cadenas del tipo 'Chapter 42' en dos partes, seleccionamos la ultima(el numero) y eso lo usamos para ordenadar

    # Ordenar la lista utilizando el número extraído
    chapter_list = sorted(chapter_list, key=extract_number, reverse=True)
     
    # Buscamos los nuevos capitulos
    new_chapters = __mangadex_search_new_chapters(chapter_list, last_chapter, url)

    # Si se ha encontrado algun capitulo nuevo lo actualizamos en la base de datos
    if len(new_chapters)>0:
        dbu.update_last_chapter(url, new_chapters)
    
    return new_chapters

def __find_a_mangaplus_chapters(chapters_list):
    output = [] # Capitulos validos - Aquellos que empiezan por 'Ch. '
    start_pattern = "Ch. "
    end_pattern = " - "
    for chapter in chapters_list:
        text = chapter.text[1:] # Quitamos el espacio inicial

        # Buscamos el patron(Ejemplo): Ch. 56 - It's a Wrap
        number = find_text_between_patterns(text, start_pattern, end_pattern)

        # Si no se ha encontrado, el patron es el siguiente(Ejemplo): Ch. 56 
        if len(number) == 0:
            number = find_text_between_patterns(text, start_pattern, "")

        if len(number) > 0:
            entry = "Chapter "+ number[0]
            output.append(entry)

    return output

def __find_span_mangaplus_chapters(chapters_list):
    output = []
    for chapter in chapters_list:
        output.append(chapter.text)

    return output

def __mangadex_search_new_chapters(chapters_list, last_chapter, mangadex_url):
    new_chapters = {}
    for chapter in chapters_list:
        # Si encontramos el ultimo capitulo leido hemos terminado o si hemos consultado los 3 ultimos capitulos disponibles
        if last_chapter == chapter: 
            break

        # Aniadimos el nombre del nuevo capitulo y su enlace, en este caso el enlace del cap no aparece
        new_chapters[chapter] = mangadex_url
    
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

def find_text_between_patterns(text, start_pattern, end_pattern):
    """
    Encuentra el texto entre dos patrones en una cadena de texto.

    Parámetros:
    - text (str): La cadena de texto en la que se realizará la búsqueda.
    - start_pattern (str): El patrón de inicio.
    - end_pattern (str): El patrón de fin.

    Retorna:
    - matches (list): Una lista de coincidencias encontradas entre los patrones.
    """
    matches = []

    # Escapamos los patrones para asegurarnos de que son tratados como texto literal.
    if end_pattern != "":
        regex_pattern = re.escape(start_pattern) + "(.*?)" + re.escape(end_pattern)
        # Usamos re.findall() para encontrar todas las coincidencias entre los patrones.
        # El uso de re.DOTALL permite que el punto coincida con cualquier carácter, incluyendo saltos de línea.
        matches = re.findall(regex_pattern, text, re.DOTALL)
    else:
        # Error en caso de que el texto sea menor al patron inicial
        try:
            start_text = text[0:len(start_pattern)]
            if start_pattern == start_text:
                matches = [text[len(start_pattern):]]
        except:
            pass
    
    # Devolvemos la lista de coincidencias.
    return matches

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


        