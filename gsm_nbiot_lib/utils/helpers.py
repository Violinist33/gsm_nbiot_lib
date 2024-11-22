# gsm_nbiot_lib/utils/helpers.py

import binascii
import utime
from machine import Pin, deepsleep, lightsleep


def hexStr_to_str(hex_str):
    """
    Преобразует строку из шестнадцатеричного формата в обычную строку.
    """
    try:
        return binascii.unhexlify(hex_str.encode('utf-8')).decode('utf-8')
    except binascii.Error:
        return ""


def str_to_hexStr(string):
    """
    Преобразует обычную строку в шестнадцатеричную строку.
    """
    return binascii.hexlify(string.encode('utf-8')).decode('utf-8')


def save_state(filename, variable, mode='w'):
    """
    Сохраняет значение переменной в файл.

    Args:
        filename: Имя файла.
        variable: Значение переменной.
        mode: Режим открытия файла ('w' для записи, 'a' для добавления).
    """
    with open(filename, mode) as f:
        f.write(str(variable))


def load_state(filename):
    """
    Загружает значение переменной из файла.

    Если файл не существует, создает его и записывает значение по умолчанию (0).

    Args:
        filename: Имя файла.

    Returns:
        Значение переменной (строка).
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError:
        save_state(filename, 0)  # Создаем файл и записываем default_value
        return '0'


def sleep_fn(time_min):
    """
    Переходит в глубокий сон на заданное количество минут.

    Args:
        time_min: Время сна в минутах.
    """
    # # power down the board
    # powerDown(pwr_en)

    print("Sleeping...")
    deepsleep(int(60000 * time_min))


def led_blink(led_onboard, num_blinks=4, time_between=0.5):
    """
    Мигает встроенным светодиодом заданное количество раз.

    Args:
        led_onboard: Объект Pin для встроенного светодиода.
        num_blinks: Количество миганий. По умолчанию - 4.
        time_between: Время между миганиями в секундах. По умолчанию - 0.5.
    """
    print("blink")

    prev = led_onboard.value()

    for _ in range(num_blinks):
        led_onboard.value(1)
        utime.sleep(time_between)
        led_onboard.value(0)
        utime.sleep(time_between)

    led_onboard.value(prev)
