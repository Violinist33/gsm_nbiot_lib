from .commands import ATCommand, ATCommandError
from machine import UART
import binascii  # Добавьте этот импорт в начало файла


class SIM7020:
    """Class for controlling the SIM7020 module using AT commands."""

    def __init__(self, uart: UART, baudrate: int = 9600, timeout: int = 1):
        """
        Initializes the SIM7020 with the specified UART and parameters.

        Args:
            uart (UART): UART instance for communication.
            baudrate (int, optional): Data transmission rate. Defaults to 9600.
            timeout (int, optional): Response timeout. Defaults to 1.
        """
        # Инициализирует ATCommand с переданным UART объектом
        self.at_command: ATCommand = ATCommand(uart, baudrate, timeout)

    def initialize(self) -> None:
        """
        Performs the initial configuration of the module: checks the connection and sets initial parameters.

        Raises:
            ATCommandError: If connection to the SIM7020 module cannot be established.
        """
        # Проверяет статус соединения и вызывает исключение, если соединение не установлено
        if not self.at_command.check_connection():
            raise ATCommandError("Failed to establish connection with SIM7020 module")

        print("SIM7020 module successfully connected")
        self.enable_rf()  # Включение RF

    def enable_rf(self) -> None:
        """
        Включает радиомодуль RF, отправляя команду AT+CFUN=1.
        """
        try:
            self.at_command.send_command("AT+CFUN=1", expected_response="OK", delay=1)
            print("AT+CFUN=1 успешно отправлена")
        except ATCommandError as e:
            print(f"Ошибка при отправке AT+CFUN=1: {e}")
            # Можно добавить дополнительную обработку, например, повторные попытки

    def set_apn(self, apn: str) -> None:
        """
        Sets the APN for network connection.

        Args:
            apn (str): APN name for the network.
        """
        # Отправляет команду для установки APN
        self.at_command.set_apn(apn)
        print(f"APN '{apn}' successfully set")

    def connect_network(self) -> None:
        """
        Connects the module to the NB-IoT network.
        """
        # Отправляет команду для подключения к сети
        self.at_command.connect_network()
        print("Network connection established")

    def disconnect_network(self) -> None:
        """
        Disconnects the module from the NB-IoT network.
        """
        # Отправляет команду для отключения от сети
        self.at_command.disconnect_network()
        print("Network disconnection completed")

    def get_signal_quality(self) -> tuple[int, int]:
        """
        Retrieves the signal quality metrics from the module.

        Returns:
            tuple[int, int]: RSSI (Received Signal Strength Indicator) and BER (Bit Error Rate).
        """
        # Получает значения RSSI и BER
        rssi: int
        ber: int
        rssi, ber = self.at_command.get_signal_quality()
        print(f"Signal quality: RSSI={rssi}, BER={ber}")
        return rssi, ber

    def send_data(self, data: str) -> None:
        """
        Sends data through the module.

        Args:
            data (str): Data to be sent through the SIM7020 module.

        Raises:
            ATCommandError: If an error occurs during data transmission.
        """
        try:
            # Отправляет команду для передачи данных
            self.at_command.send_command(f'AT+SEND={data}', expected_response="SEND OK")
            print("Data successfully sent")
        except ATCommandError:
            print("Error occurred while sending data")

    def close(self) -> None:
        """
        Terminates usage of the module and closes the UART connection.
        """
        # Закрывает интерфейс AT команд и завершает соединение
        self.at_command.close()
        print("Connection with the module closed")

    def mqtt_new(self, broker_address: str, port: int = 1883, keepalive: int = 12000, buffer_size: int = 1024):
        """
        Создает новое MQTT-соединение.

        Args:
            broker_address (str): Адрес MQTT-брокера.
            port (int, optional): Порт для подключения. Defaults to 1883.
            keepalive (int, optional): Интервал keepalive. Defaults to 12000.
            buffer_size (int, optional): Размер буфера. Defaults to 1024.
        """
        cmd = f'AT+CMQNEW="{broker_address}","{port}",{keepalive},{buffer_size}'
        self.at_command.send_command(cmd, expected_response="OK")
        print("MQTT-соединение создано")

    def mqtt_connect(self, client_id: str, clean_session: int = 1, keepalive: int = 12000, username: str = "",
                     password: str = ""):
        """
        Подключается к MQTT-брокеру.

        Args:
            client_id (str): Идентификатор клиента.
            clean_session (int, optional): Флаг чистой сессии. Defaults to 1.
            keepalive (int, optional): Интервал keepalive. Defaults to 12000.
            username (str, optional): Имя пользователя. Defaults to "".
            password (str, optional): Пароль. Defaults to "".
        """
        cmd = f'AT+CMQCON=0,{clean_session},"{client_id}",{keepalive},1,0,"{username}","{password}"'
        self.at_command.send_command(cmd, expected_response="OK")
        print("Подключение к MQTT-брокеру выполнено")

    def mqtt_publish(self, topic: str, message: str, qos: int = 1, retain: int = 0):
        """
        Публикует сообщение в MQTT-топик.

        Args:
            topic (str): Топик для публикации.
            message (str): Сообщение для отправки.
            qos (int, optional): QoS уровень. Defaults to 1.
            retain (int, optional): Флаг retain. Defaults to 0.
        """
        hex_message = binascii.hexlify(message.encode()).decode()
        hex_length = len(hex_message)
        cmd = f'AT+CMQPUB=0,"{topic}",{qos},{retain},0,{hex_length},"{hex_message}"'
        self.at_command.send_command(cmd, expected_response="OK")
        print(f"Сообщение опубликовано в топик {topic}: {message}")

    def mqtt_subscribe(self, topic: str, qos: int = 1):
        """
        Подписывается на MQTT-топик.

        Args:
            topic (str): Топик для подписки.
            qos (int, optional): QoS уровень. Defaults to 1.
        """
        cmd = f'AT+CMQSUB=0,"{topic}",{qos}'
        self.at_command.send_command(cmd, expected_response="OK")
        print(f"Подписка на топик {topic} выполнена")
