FROM ubuntu:22.04

USER root

RUN apt -y update
RUN apt -y install wget tar bzip2
RUN apt -y install libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-6 libxrender1 libasound2 libpango-1.0-0 libavcodec58 libavformat58 libavutil56

# Instalamos Firefox pero sin usar apt/version snap (No es compatible, no se comunica de forma correcta con geckodriver)
WORKDIR /tmp
RUN wget -O firefox-latest.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" 
RUN tar xjf firefox-latest.tar.bz2 
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

# Copy the requirements in app folder and install them (To create new cache files and not copy project cache files)
WORKDIR /opt/app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy project content to app folder
COPY . /opt/app

EXPOSE 8081
CMD ["python3", "main.py"]
