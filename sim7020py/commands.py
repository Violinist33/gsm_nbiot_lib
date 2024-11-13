# src/gsm_serial_lib/commands.py

import time
import serial  # Предполагается, что библиотека PySerial используется для UART


class ATCommandError(Exception):
    """Исключение для ошибок AT-команд"""
    pass


class ATCommand:
    """Класс для отправки и обработки AT-команд к модулю SIM7020 через UART."""

    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Инициализация подключения к модулю через UART.

        :param port: Порт UART (например, "/dev/ttyUSB0" для Linux)
        :param baudrate: Скорость передачи данных
        :param timeout: Таймаут ожидания ответа
        """
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, command, expected_response="OK", delay=0.5):
        """
        Отправка AT-команды и ожидание ответа.

        :param command: AT-команда для отправки
        :param expected_response: Ожидаемый ответ (по умолчанию "OK")
        :param delay: Задержка перед чтением ответа
        :return: Ответ от модуля
        """
        # Очистка буфера и отправка команды
        self.serial.reset_input_buffer()
        self.serial.write((command + "\r\n").encode())

        time.sleep(delay)
        response = self.serial.readlines()

        # Преобразуем байты в строки и убираем лишние символы
        response = [line.decode().strip() for line in response]

        # Проверка на ожидаемый ответ
        if expected_response not in response:
            raise ATCommandError(f"Не удалось получить ожидаемый ответ: {expected_response}")

        return response

    def check_connection(self):
        """
        Проверка соединения с модулем через команду AT.

        :return: True, если модуль отвечает, иначе False
        """
        try:
            response = self.send_command("AT")
            return "OK" in response
        except ATCommandError:
            return False

    def get_signal_quality(self):
        """
        Запрос уровня сигнала у модуля (команда AT+CSQ).

        :return: Уровень сигнала (включает RSSI и BER)
        """
        response = self.send_command("AT+CSQ")

        # Ожидаем, что ответ будет в формате "+CSQ: <rssi>,<ber>"
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = signal_info.split(",")
                return int(rssi), int(ber)

        raise ATCommandError("Не удалось получить уровень сигнала")

    def set_apn(self, apn):
        """
        Установка APN (Access Point Name) для подключения к сети.

        :param apn: Название APN
        :return: None
        """
        self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')

    def connect_network(self):
        """
        Подключение к сети (команда AT+CGATT=1).

        :return: None
        """
        self.send_command("AT+CGATT=1")

    def disconnect_network(self):
        """
        Отключение от сети (команда AT+CGATT=0).

        :return: None
        """
        self.send_command("AT+CGATT=0")

    def close(self):
        """
        Закрытие соединения с UART.
        """
        self.serial.close()
