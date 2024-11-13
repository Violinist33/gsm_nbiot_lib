# src/gsm_serial_lib/blynk_integration.py
#sim7020py/blynk_integration.py

from .sim7020 import SIM7020
import time
import logging

logging.basicConfig(level=logging.INFO)


class BlynkIntegration:
    """Класс для интеграции с платформой Blynk через SIM7020."""

    def __init__(self, port, apn, blynk_token, baudrate=9600, timeout=1, max_retries=3):
        """
        Инициализация Blynk-интеграции с настройкой APN и токена.

        :param port: Порт UART для SIM7020 (например, "/dev/ttyUSB0" для Linux)
        :param apn: Название APN для подключения к сети
        :param blynk_token: Токен доступа Blynk
        :param baudrate: Скорость передачи данных по UART
        :param timeout: Таймаут ожидания ответа
        :param max_retries: Максимальное количество попыток при сбое отправки/получения данных
        """
        self.sim7020 = SIM7020(port, baudrate, timeout)
        self.apn = apn
        self.blynk_token = blynk_token
        self.max_retries = max_retries
        self.connected = False

    def connect(self):
        """
        Подключение к сети и инициализация соединения с Blynk.
        """
        try:
            self.sim7020.initialize()
            self.sim7020.set_apn(self.apn)
            self.sim7020.connect_network()
            self.connected = True
            logging.info("Соединение с сетью и Blynk установлено")
        except Exception as e:
            logging.error(f"Ошибка подключения: {e}")
            self.connected = False

    def ensure_connection(self):
        """
        Проверка подключения и попытка переподключения при необходимости.
        """
        if not self.connected:
            logging.info("Попытка переподключения...")
            self.connect()

    def send_value(self, virtual_pin, value):
        """
        Отправка данных на определенный виртуальный пин на Blynk-сервер.

        :param virtual_pin: Номер виртуального пина на Blynk
        :param value: Значение для отправки
        """
        self.ensure_connection()

        command = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/update/{virtual_pin}?value={value}\""
        for attempt in range(self.max_retries):
            try:
                self.sim7020.at_command.send_command(command, expected_response="OK")
                logging.info(f"Значение {value} отправлено на виртуальный пин {virtual_pin}")
                return
            except Exception as e:
                logging.warning(f"Попытка {attempt + 1} не удалась: {e}")
                time.sleep(1)  # Небольшая пауза перед повторной попыткой

        logging.error(
            f"Не удалось отправить значение на виртуальный пин {virtual_pin} после {self.max_retries} попыток")

    def get_value(self, virtual_pin):
        """
        Получение данных с определенного виртуального пина на Blynk-сервере.

        :param virtual_pin: Номер виртуального пина на Blynk
        :return: Полученное значение или None при ошибке
        """
        self.ensure_connection()

        command = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/get/{virtual_pin}\""
        for attempt in range(self.max_retries):
            try:
                response = self.sim7020.at_command.send_command(command, expected_response="OK")
                data = response[-1].split()[-1]  # Пример парсинга ответа
                logging.info(f"Получено значение {data} с виртуального пина {virtual_pin}")
                return data
            except Exception as e:
                logging.warning(f"Попытка {attempt + 1} не удалась: {e}")
                time.sleep(1)

        logging.error(f"Не удалось получить данные с виртуального пина {virtual_pin} после {self.max_retries} попыток")
        return None

    def disconnect(self):
        """
        Отключение от Blynk и сети NB-IoT.
        """
        self.sim7020.disconnect_network()
        self.connected = False
        logging.info("Отключено от Blynk и сети NB-IoT")

    def close(self):
        """
        Завершение работы с модулем SIM7020.
        """
        self.sim7020.close()
        logging.info("Закрыто соединение с SIM7020")
