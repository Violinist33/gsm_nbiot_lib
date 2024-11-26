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
PORT = "1883"
CLIENTID = "Client_1"
DEVICE_NAME = env.get("DEVICE_NAME", "Vertexyz")
DEVICE_SECRET = env.get("DEVICE_SECRET", "J45_VVZsA5w6uw5MI4X095f37GpZAJ0N")

# Аппаратная конфигурация
LED_ONBOARD_PIN = 25  # Встроенный светодиод
LED_MAIN_PIN = 2  # Внешний светодиод
PWR_EN_PIN = 14  # Пин для управления питанием SIM7020
UART_PORT = 0  # Выбор UART0 (используйте 1 для UART1)
UART_BAUDRATE = 115200  # Скорость передачи данных
