# gsm_nbiot_lib/utils/logger.py

import utime


def log(message):
    """
    Logs a message with a timestamp.

    Args:
        message (str): Message to be logged.

    Example:
        log("Device started.")
        Output:
            [12:30:45] Device started.
    """
    timestamp = utime.localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
    print(f"[{formatted_time}] {message}")


def error_log(error_message):
    """
    Logs an error message with a timestamp.

    Args:
        error_message (str): Error message to be logged.

    Example:
        error_log("Failed to connect to MQTT broker.")
        Output:
            [12:31:00] ERROR: Failed to connect to MQTT broker.
    """
    timestamp = utime.localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
    print(f"[{formatted_time}] ERROR: {error_message}")


def debug_log(debug_message):
    """
    Logs a debug message with a timestamp.

    Args:
        debug_message (str): Debug message to be logged.

    Example:
        debug_log("Attempting to reconnect.")
        Output:
            [12:31:05] DEBUG: Attempting to reconnect.
    """
    timestamp = utime.localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
    print(f"[{formatted_time}] DEBUG: {debug_message}")
