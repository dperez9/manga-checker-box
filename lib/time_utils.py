from datetime import datetime, timedelta

def seconds_until_next_hour():
    # Obtenemos la hora actual
    now = datetime.now()

    hour = now.hour + 1
    if hour==24:
        hour = 0

    # Calcula el tiempo hasta la próxima hora en punto
    next_hour = now.replace(microsecond=0, second=1, minute=0, hour=hour) # Aniadimos el 1 para que empiece a en punto y no milisegundos antes. Ejemplo: 09:59:59.997
    remain_time = next_hour - now

    # Devuelve el tiempo restante como un objeto timedelta
    return int(remain_time.total_seconds())

