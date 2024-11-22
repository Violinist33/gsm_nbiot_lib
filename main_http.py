from sim7020py import ATCommandError, SIM7020, BlynkIntegration, save_state, load_state, parse_response
import utime
from machine import Pin, UART, deepsleep, lightsleep

from config import *

# Инициализация светодиодов и пина управления питанием
led_onboard = Pin(LED_PIN, Pin.OUT)
led_main = Pin(LED_PIN_MAIN, Pin.OUT)
pwr_key = Pin(PWR_EN, Pin.OUT)

# Инициализация UART с правильными пинами и увеличенным таймаутом
# Для UART0 используйте GP0 (TX) и GP1 (RX)
# Для UART1 используйте GP4 (TX) и GP5 (RX)
if UART_PORT == 0:
    uart_tx = Pin(0)
    uart_rx = Pin(1)
elif UART_PORT == 1:
    uart_tx = Pin(4)
    uart_rx = Pin(5)
else:
    raise ValueError("Invalid UART_PORT. Use 0 for UART0 or 1 for UART1.")

uart = UART(UART_PORT, baudrate=UART_BAUDRATE, tx=uart_tx, rx=uart_rx, timeout=5000)  # Установлен таймаут 5 секунд
print(uart)

# Создание экземпляров SIM7020 и BlynkIntegration с увеличенным таймаутом
sim_7020 = SIM7020(uart=uart, baudrate=UART_BAUDRATE, timeout=5)
blynk = BlynkIntegration(uart=uart, apn=APN, blynk_token=BLYNK_TOKEN, timeout=5)


# Функции управления питанием SIM7020
def power_on():
    pwr_key.value(1)
    utime.sleep(2)  # Ожидание полной инициализации модуля


def power_off():
    pwr_key.value(0)
    utime.sleep(1)  # Ожидание отключения питания


# Функция мигания светодиодом
def led_blink(num_blinks=4, time_between=0.5):
    """Мигает встроенным светодиодом заданное количество раз."""
    print("blink")
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
    sim_7020.initialize()
    sim_7020.set_apn(APN)
    try:
        # Отправка команды AT+CFUN=1 для включения RF
        sim_7020.at_command.send_command("AT+CFUN=1", expected_response="OK", delay=1)
        print("AT+CFUN=1 успешно отправлена")
    except ATCommandError as e:
        print(f"Ошибка при отправке AT+CFUN=1: {e}")
    sim_7020.connect_network()
    blynk.connect()


# Функция парсинга ответа от AT команды
def parse_at_response(response):
    command_name, parameters = parse_response(response)
    print("Имя команды:", command_name)
    print("Параметры:", parameters)


# Функция отправки и обработки AT команды
def send_and_process(cmd):
    try:
        response = sim_7020.at_command.send_command(cmd)
        parse_at_response(response)
    except ATCommandError as e:
        print(f"Ошибка: {e}")


# Настройка MQTT подключения
def mqtt_connect():
    send_and_process("AT+CSQ")  # Проверка качества сигнала
    send_and_process(f'AT+CMQNEW="{BROKER_ADDRESS}","1883",12000,1024')
    send_and_process(f'AT+CMQCON=0,3,"{DEVICE_NAME}",45,1,0,"device","{DEVICE_SECRET}"')


# Управление состоянием лампы
def toggle_lamp_state(state_file='state.db'):
    current_state = load_state(state_file)
    lamp_is_on = int(current_state) if current_state else 1
    led_main.value(lamp_is_on)
    led_onboard.value(not lamp_is_on)
    return lamp_is_on


# Основная функция программы
def main():
    # Инициализация подключения и настройка Blynk
    initialize_connection()
    lamp_is_on = toggle_lamp_state()

    # Мигание светодиодом при старте
    led_blink(5)

    # Главный цикл
    while True:
        print("Проверка команд...")
        # Запрос значения виртуального пина от Blynk
        blynk.get_value(0)  # Передаём целочисленное значение вместо строки

        # Переключение состояния светодиодов на основе состояния лампы
        lamp_is_on = not lamp_is_on
        save_state('state.db', lamp_is_on)
        led_main.value(lamp_is_on)
        led_onboard.value(not lamp_is_on)
        utime.sleep(2)  # Задержка

        # Пример отправки и получения данных через MQTT (если необходимо)
        mqtt_connect()

        # Переход в режим низкого энергопотребления
        print("Переход в режим светового сна...")
        led_blink(4, 0.5)
        lightsleep(10000)  # Световой сон на 10 секунд
        led_blink(10, 0.05)

    # Отключение при завершении
    power_off()
    print("Устройство переходит в глубокий сон...")
    deepsleep(15 * 60000)  # Глубокий сон на 15 минут


if __name__ == "__main__":
    main()
