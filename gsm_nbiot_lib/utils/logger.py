# gsm_nbiot_lib/utils/logger.py

import utime

def log(message):
    timestamp = utime.localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
    print(f"[{formatted_time}] {message}")
