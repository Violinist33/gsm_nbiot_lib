"""
Модуль для взаємодії з AT-командами через UART.

Цей модуль надає функціонал для відправки AT-команд до пристрою через UART
і обробки отриманих відповідей.

Класи:
    - ATCommandInterface: Інтерфейс для відправлення AT-команд і отримання відповідей.

Функції:
    В межах класу ATCommandInterface:
        - __init__: Ініціалізує UART-з'єднання.
        - send_command: Відправляє AT-команду та отримує відповідь.
        - wait_response_line: Очікує на рядок відповіді з UART.

Імпорти:
    - utime: Використовується для роботи з часом.
    - machine.UART: Для ініціалізації UART-з'єднання.
    - gsm_nbiot_lib.core.command_parser.parse_response: Для парсингу відповідей.
    - gsm_nbiot_lib.core.errors.ATCommandError: Виняток для помилок AT-команд.
    - gsm_nbiot_lib.utils.helpers.sleep_fn: Допоміжна функція для затримки.
"""

import utime
from machine import UART
from gsm_nbiot_lib.core.command_parser import parse_response
from gsm_nbiot_lib.core.errors import ATCommandError
from gsm_nbiot_lib.utils.helpers import sleep_fn
from gsm_nbiot_lib.models.command import info_cmd


class ATCommandInterface:
    """
    Інтерфейс для роботи з AT-командами через UART.

    Атрибути:
        uart (UART): Об'єкт UART для передачі даних.
        timeout (int): Таймаут очікування відповіді в мілісекундах.

    Методи:
        - __init__(uart_port, baudrate, timeout): Ініціалізує UART.
        - send_command(cmd, attempts, sleep_on_error): Відправляє команду та отримує відповідь.
        - wait_response_line(): Очікує на рядок відповіді.
    """

    def __init__(self, uart_port=0, baudrate=115200, timeout=5000):
        """
        Ініціалізація UART-з'єднання.

        Аргументи:
            uart_port (int): Номер UART-порту. За замовчуванням 0.
            baudrate (int): Швидкість передачі даних. За замовчуванням 115200.
            timeout (int): Таймаут очікування відповіді в мілісекундах. За замовчуванням 5000.
        """
        self.uart = UART(uart_port, baudrate=baudrate, bits=8, parity=None, stop=1)
        self.timeout = timeout

    def send_command(self, cmd, attempts=5, sleep_on_error=True):
        """
        Відправляє AT-команду та очікує на відповідь.

        Аргументи:
            cmd (str): AT-команда для відправлення.
            attempts (int): Кількість спроб у разі невдачі. За замовчуванням 5.
            sleep_on_error (bool): Затримка перед підняттям винятку. За замовчуванням True.

        Повертає:
            tuple: Назва команди та її параметри.

        Піднімає:
            ATCommandError: Якщо відповідь містить "ERROR" або "TIMEOUT".
        """
        response = ""
        for attempt in range(attempts):
            print(f"Attempt {attempt + 1}: {cmd}")
            self.uart.write((cmd + '\r\n').encode())
            response = self.wait_response_line()
            if response and response not in ["ERROR", "TIMEOUT"]:
                break
            utime.sleep(1)

        if sleep_on_error and response in ["ERROR", "TIMEOUT"]:
            sleep_fn(0.1)
            raise ATCommandError(f"Command '{cmd}' failed with response: {response}")

        command_name, parameters = parse_response(response)
        if parameters:
            info_cmd(command_name, parameters)
        return command_name, parameters

    def wait_response_line(self, timeout=5000):
        """
        Очікує на відповідь від пристрою через UART.

        Повертає:
            str: Рядок відповіді, або спеціальні значення "ERROR" чи "TIMEOUT".

        Примітки:
            - Завершує читання, якщо виявлено "OK", "ERROR" або "TIMEOUT" у відповіді.
        """
        response = ""
        start_time = utime.ticks_ms()
        while (utime.ticks_ms() - start_time) < timeout:
            if self.uart.any():
                char = self.uart.read(1).decode()
                response += char
                if response.endswith("OK\r\n") or response.endswith("ERROR\r\n") or response.endswith("TIMEOUT\r\n"):
                    break
        if response.endswith("OK\r\n"):
            return response
        elif response.endswith("ERROR\r\n"):
            return "ERROR"
        elif response.endswith("TIMEOUT\r\n") or not response:
            return "TIMEOUT"
        return response
