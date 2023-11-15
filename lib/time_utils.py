from datetime import datetime, timedelta

def seconds_until_next_hour():
    # Obtenemos la hora actual
    now = datetime.now()

    # Calcula el tiempo hasta la próxima hora en punto
    next_hour = now.replace(microsecond=0, second=0, minute=0, hour=now.hour + 1)
    remain_time = next_hour - now

    # Devuelve el tiempo restante como un objeto timedelta
    return int(remain_time.total_seconds())
