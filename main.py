from gsm_nbiot_lib import SIM7020, MQTTClient, led_blink, handle_mqtt_publish
# from gsm_nbiot_lib.core.command_parser import handle_mqtt_publish
from machine import Pin, lightsleep, freq
import utime

print("Frequency: ", freq())

# Налаштування
APN = "nbiot"
Broker_Address = "blynk.cloud"
Port = "1883"
ClientID = "Client_1"
DeviceSecret = "J45_VVZsA5w6uw5MI4X095f37GpZAJ0N"

# Піни
LED_ONBOARD_PIN = 25
LED_MAIN_PIN = 2
PWR_EN_PIN = 14
UART_PORT = 0
UART_BAUDRATE = 115200

# Ініціалізація світлодіодів
led_onboard = Pin(LED_ONBOARD_PIN, Pin.OUT)
led_main = Pin(LED_MAIN_PIN, Pin.OUT)

# Ініціалізація модуля SIM7020
sim7020 = SIM7020(UART_PORT, UART_BAUDRATE, APN, PWR_EN_PIN)

# Включення живлення
sim7020.power_on(PWR_EN_PIN)
utime.sleep(2)

# Конфігурація APN
sim7020.configure_apn()

# Перевірка якості сигналу
sim7020.check_signal_quality()
print(f"Signal Quality: {sim7020.signal_quality}")

# Ініціалізація MQTT клієнта
mqtt_client = MQTTClient(
    sim7020.at,
    Broker_Address,
    Port,
    ClientID,
    DeviceSecret
)

# Підключення до MQTT
mqtt_client.connect()

# Підписка на топік
mqtt_client.subscribe("downlink/ds/Integer V0")

# Основний цикл
while True:
    print("Main loop working...")

    # Запит значення піна
    name_cmd, response = mqtt_client.publish("get/ds", "Integer V0")

    # Обробка відповіді
    handle_mqtt_publish(led_main, led_onboard, response)

    # Блимання світлодіодами
    led_blink(led_onboard, 4, 0.5)

    # Режим світлового сну
    lightsleep(10000)

    # Блимання швидкими імпульсами
    led_blink(led_onboard, 10, 0.05)

    # # Затримка перед наступною ітерацією
    # utime.sleep(3)

    # При необхідності можна додати умови для виходу з циклу та інших дій

# except KeyboardInterrupt:
#     # Роз'єднання при завершенні
#     # mqtt_client.disconnect()  # Використовуйте метод disconnect замість sendCMD_waitRespLine
#     # Сон на 15 хв
#     # sleep_fn(15)
