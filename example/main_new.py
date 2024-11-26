from sim7020py import SIM7020, BlynkIntegration, save_state, load_state, ATCommandError
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
    try:
        blynk.connect()
        print("Инициализация подключения выполнена успешно")
    except ATCommandError as e:
        print(f"Ошибка при инициализации подключения: {e}")

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
    lamp_is_on = toggle_lamp_state()

    # Установка начального состояния светодиодов
    led_blink(5)

    # Инициализация подключения к сети и Blynk
    initialize_connection()

    # Подключение к MQTT брокеру
    sim7020.mqtt_new(broker_address=BROKER_ADDRESS, port=1883, keepalive=12000, buffer_size=1024)
    sim7020.mqtt_connect(client_id=DEVICE_NAME, clean_session=1, keepalive=12000, username="device", password=DEVICE_SECRET)

    # Подписка на топик для управления лампой
    sim7020.mqtt_subscribe("downlink/ds/Integer V0")

    while True:
        print("Работаем...")
        # Запрос значения виртуального пина от Blynk
        value = blynk.get_value(0)  # Получение значения из Blynk
        if value is not None:
            print(f"Получено значение от Blynk: {value}")
            # Здесь можно добавить логику обработки полученного значения

        # Переключение состояния светодиодов на основе состояния лампы
        lamp_is_on = not lamp_is_on
        save_state('state.db', lamp_is_on)
        led_main.value(lamp_is_on)
        led_onboard.value(not lamp_is_on)
        print(f"Лампа {'Включена' if lamp_is_on else 'Выключена'}")

        # Отправка MQTT сообщения о состоянии лампы
        sim7020.mqtt_publish("ds/LampStatus", str(lamp_is_on))

        # Переход в режим низкого энергопотребления
        print("Переход в режим светового сна...")
        led_blink(4, 0.5)
        lightsleep(10000)  # Световой сон на 10 секунд
        led_blink(10, 0.05)

    # Отключение от MQTT брокера и переход в глубокий сон
    sim7020.mqtt_disconnect()
    print("Устройство переходит в глубокий сон на 15 минут...")
    sleep_fn(15)

if __name__ == "__main__":
    main()
