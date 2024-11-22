from sim7020py import SIM7020, BlynkIntegration, save_state, load_state, parse_response, ATCommandError
import utime
import binascii
from machine import Pin, UART, deepsleep, lightsleep

from config import *

# Инициализация светодиодов и пина управления питанием
led_onboard = Pin(LED_PIN, Pin.OUT)
led_main = Pin(LED_PIN_MAIN, Pin.OUT)
pwr_en = Pin(PWR_EN, Pin.OUT)

# Инициализация UART
if UART_PORT == 0:
    uart_tx = Pin(0)
    uart_rx = Pin(1)
elif UART_PORT == 1:
    uart_tx = Pin(4)
    uart_rx = Pin(5)
else:
    raise ValueError("Неверный UART_PORT. Используйте 0 для UART0 или 1 для UART1.")

uart = UART(UART_PORT, baudrate=UART_BAUDRATE, tx=uart_tx, rx=uart_rx, timeout=5000)
print(uart)

# Создание экземпляров SIM7020 и BlynkIntegration
sim7020 = SIM7020(uart=uart, baudrate=UART_BAUDRATE, timeout=5)
blynk = BlynkIntegration(uart=uart, apn=APN, blynk_token=BLYNK_TOKEN, baudrate=UART_BAUDRATE, timeout=5)


# Функции управления питанием SIM7020
def power_on():
    pwr_en.value(1)
    utime.sleep(2)  # Ожидание полной инициализации модуля


def power_off():
    pwr_en.value(0)
    utime.sleep(1)  # Ожидание отключения питания


# Функция мигания светодиодом
def led_blink(num_blinks=4, time_between=0.5):
    """Мигает встроенным светодиодом заданное количество раз."""
    print("Мигаем светодиодом...")
    prev = led_onboard.value()
    for _ in range(num_blinks):
        led_onboard.value(1)
        utime.sleep(time_between)
        led_onboard.value(0)
        utime.sleep(time_between)
    led_onboard.value(prev)


# Функция инициализации подключения к сети и Blynk
def initialize_connection():
    power_on()
    blynk.connect()


# Функция парсинга ответа от AT команды
def parse_at_response(response):
    command_name, parameters = parse_response(response)
    print("Имя команды:", command_name)
    print("Параметры:", parameters)
    return command_name, parameters


# Функция отправки и обработки AT команды
def send_and_process(cmd, expected_response="OK"):
    try:
        response = sim7020.at_command.send_command(cmd, expected_response=expected_response)
        command_name, parameters = parse_at_response(response)
        return command_name, parameters
    except ATCommandError as e:
        print(f"Ошибка: {e}")
        return None, None


# Функция подключения к MQTT брокеру
def mqtt_connect():
    send_and_process("AT+CSQ")  # Проверка качества сигнала
    send_and_process(f'AT+CMQNEW="{BROKER_ADDRESS}","1883",12000,1024')
    send_and_process(f'AT+CMQCON=0,3,"{DEVICE_NAME}",45,1,0,"device","{DEVICE_SECRET}"')
    print("Подключение к MQTT брокеру выполнено")


# Функция отключения от MQTT брокера
def mqtt_disconnect():
    send_and_process("AT+CMQDISCON=0", expected_response="OK")
    print("Отключение от MQTT брокера выполнено")


# Функция отправки MQTT сообщения
def send_message(pin_name, value):
    """
    Отправляет MQTT сообщение на указанный топик с заданным значением.

    Args:
        pin_name (str): Название пина (например, "Voltage", "Temperature").
        value (str | int): Значение для отправки.
    """
    topic = f'ds/{pin_name}'
    hex_value = binascii.hexlify(str(value).encode()).decode()
    hex_length = len(hex_value)
    command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_value}"'
    send_and_process(command, expected_response="OK")
    print(f"Сообщение отправлено на топик {topic}: {value}")


# Функция подписки на MQTT топик
def subscribe_to_pin(pin_name):
    """
    Подписывается на MQTT топик для получения данных с указанного пина.

    Args:
        pin_name (str): Название пина (например, "Integer V0").
    """
    topic = f'downlink/ds/{pin_name}'
    command = f'AT+CMQSUB=0,"{topic}",1'
    send_and_process(command, expected_response="OK")
    print(f"Подписка на топик {topic} выполнена")


# Функция запроса значения пина через MQTT
def request_pin_value(pin_name):
    """
    Отправляет запрос на получение значения пина через MQTT.

    Args:
        pin_name (str): Название пина (например, "Integer V0").
    """
    topic = "get/ds"  # Топик для запросов
    hex_name = binascii.hexlify(pin_name.encode()).decode()
    hex_length = len(hex_name)
    command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_name}"'
    send_and_process(command, expected_response="OK")
    print(f"Запрос значения пина {pin_name} отправлен")


# Функция переключения состояния лампы
def toggle_lamp_state(state_file='state.db'):
    current_state = load_state(state_file)
    lamp_is_on = int(current_state) if current_state else 1
    led_main.value(lamp_is_on)
    led_onboard.value(not lamp_is_on)
    return lamp_is_on


# Функция перехода в режим сна
def sleep_fn(time_minutes):
    # Отключение питания SIM7020
    power_off()
    print("Переход в режим сна...")
    utime.sleep(2)
    deepsleep(time_minutes * 60000)  # Глубокий сон на заданное количество минут


# Основная функция программы
def main():
    # Загрузка состояния лампы из файла
    loaded_state = load_state('state.db')
    lamp_is_on = int(loaded_state) if loaded_state else 1

    # Установка начального состояния светодиодов
    led_main.value(lamp_is_on)
    led_onboard.value(not lamp_is_on)
    led_blink(5)

    # Инициализация подключения к сети и Blynk
    initialize_connection()

    # Подключение к MQTT брокеру
    mqtt_connect()

    # Подписка на топик для управления лампой
    subscribe_to_pin("Integer V0")

    while True: # utime.ticks_diff(utime.ticks_ms(), start_time) < 10000:  # 10 секунд = 10000 мілісекунд
        print("Работаем...")
        # Запрос значения виртуального пина от Blynk
        blynk.get_value(0)  # Передаём целочисленное значение вместо строки

        # Переключение состояния светодиодов на основе состояния лампы
        lamp_is_on = not lamp_is_on
        save_state('state.db', lamp_is_on)
        led_main.value(lamp_is_on)
        led_onboard.value(not lamp_is_on)
        print(f"Лампа {'Включена' if lamp_is_on else 'Выключена'}")

        # Отправка MQTT сообщения о состоянии лампы
        send_message("LampStatus", lamp_is_on)

        # Переход в режим низкого энергопотребления
        print("Переход в режим светового сна...")
        led_blink(4, 0.5)
        lightsleep(10000)  # Световой сон на 10 секунд
        led_blink(10, 0.05)

    # Отключение от MQTT брокера и переход в глубокий сон
    mqtt_disconnect()
    print("Устройство переходит в глубокий сон на 15 минут...")
    sleep_fn(15)


if __name__ == "__main__":
    main()
