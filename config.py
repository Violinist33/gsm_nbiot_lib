import os


def load_config(filename=".env"):
    """
    Загружает переменные конфигурации из файла.

    Args:
        filename (str): Имя файла конфигурации.

    Returns:
        dict: Словарь с переменными конфигурации.
    """
    config = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except OSError as e:
        print(f"Ошибка загрузки конфигурационного файла: {e}")
    return config


# Загрузка конфигурации
env = load_config()

# Извлечение переменных конфигурации
APN = env.get("APN", "nbiot")
BLYNK_TOKEN = env.get("BLYNK_TOKEN", "")
BROKER_ADDRESS = env.get("BROKER_ADDRESS", "blynk.cloud")
DEVICE_NAME = env.get("DEVICE_NAME", "")
DEVICE_SECRET = env.get("DEVICE_SECRET", "")

# Аппаратная конфигурация
LED_PIN = 25  # Встроенный светодиод
LED_PIN_MAIN = 2  # Внешний светодиод
PWR_EN = 14  # Пин для управления питанием SIM7020
UART_PORT = 0  # Выбор UART0 (используйте 1 для UART1)
UART_BAUDRATE = 115200  # Скорость передачи данных

# Отладочный вывод загруженной конфигурации
print("Configuration Loaded:")
print(f"APN: {APN}")
print(f"BLYNK_TOKEN: {BLYNK_TOKEN}")
print(f"BROKER_ADDRESS: {BROKER_ADDRESS}")
print(f"DEVICE_NAME: {DEVICE_NAME}")
print(f"DEVICE_SECRET: {DEVICE_SECRET}")
