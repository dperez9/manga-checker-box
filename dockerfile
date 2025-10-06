FROM ubuntu:22.04

USER root

RUN apt -y update
RUN apt -y install wget tar bzip2
RUN apt -y install libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-6 libxrender1 libasound2 libpango-1.0-0 libavcodec58 libavformat58 libavutil56
RUN apt -y update && apt -y install wget tar xz-utils ca-certificates && update-ca-certificates

# Instalamos Firefox pero sin usar apt/version snap (No es compatible, no se comunica de forma correcta con geckodriver)
WORKDIR /tmp
RUN wget -O firefox-latest.tar.xz "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" 
RUN tar xJf firefox-latest.tar.xz
RUN mv firefox /opt/firefox-latest 
RUN ln -s /opt/firefox-latest/firefox /usr/bin/firefox 
RUN rm -r /tmp/*
RUN firefox --version

# Instalar geckodriver to firefox automatization
WORKDIR /tmp
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
RUN tar -xvzf geckodriver*
# Borramos el contenido de la carpeta temporal 
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin/geckodriver
RUN rm -r /tmp/* 

# Lo aniadimos el PATH
RUN export PATH=$PATH:/usr/local/bin/geckodriver
RUN geckodriver --version

# Instalamos python
RUN apt -y install python3.10 
RUN apt -y install python3-pip

# Creamos un usuario no root (UID/GID 1000) - Creamos un grupo appgroup y le agregamos el usuario appuser con gid 1000
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

# Copy the requirements in app folder and install them (To create new cache files and not copy project cache files)
WORKDIR /opt/app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy project content to app folder
COPY . /opt/app

# Dar permisos al usuario no root
RUN chown -R appuser:appgroup /opt/app

# Damos permisos al usuario no root sobre la carpeta en la que se va alojar la BBDD
RUN mkdir -p /db && chown -R appuser:appgroup /db

# Creamos las carpetas que usara el bot para almacenar logs y le damos permisos
RUN mkdir ./logs && chown -R appuser:appgroup ./logs
RUN mkdir ./logs/bot && chown -R appuser:appgroup ./logs/bot
RUN mkdir ./logs/manga_updates && chown -R appuser:appgroup ./logs/manga_updates

# Cambiamos al usuario no root
USER appuser

EXPOSE 8081
CMD ["python3", "main.py"]
