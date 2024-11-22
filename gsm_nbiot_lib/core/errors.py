# gsm_nbiot_lib/core/errors.py

class ATCommandError(Exception):
    """Виняток для помилок AT-команд."""
    pass

class ConnectionError(Exception):
    """Виняток для помилок підключення."""
    pass
