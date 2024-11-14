from .commands import ATCommand, ATCommandError

class SIM7020:
    """Class for controlling the SIM7020 module using AT commands."""

    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Initializes the SIM7020 with specified port and UART parameters.

        :param port: UART port (e.g., "/dev/ttyUSB0" for Linux)
        :param baudrate: Data transmission rate
        :param timeout: Response timeout
        """
        self.at_command = ATCommand(port, baudrate, timeout)

    def initialize(self):
        """
        Initial configuration of the module: checks connection and sets initial parameters.

        :return: None
        """
        if not self.at_command.check_connection():
            raise ATCommandError("Failed to establish connection with SIM7020 module")

        print("SIM7020 module successfully connected")

    def set_apn(self, apn):
        """
        Sets the APN for network connection.

        :param apn: APN name
        :return: None
        """
        self.at_command.set_apn(apn)
        print(f"APN '{apn}' successfully set")

    def connect_network(self):
        """
        Connects to the NB-IoT network.

        :return: None
        """
        self.at_command.connect_network()
        print("Network connection established")

    def disconnect_network(self):
        """
        Disconnects from the NB-IoT network.

        :return: None
        """
        self.at_command.disconnect_network()
        print("Network disconnection completed")

    def get_signal_quality(self):
        """
        Retrieves the signal quality from the module.

        :return: Tuple (RSSI, BER)
        """
        rssi, ber = self.at_command.get_signal_quality()
        print(f"Signal quality: RSSI={rssi}, BER={ber}")
        return rssi, ber

    def send_data(self, data):
        """
        Sends data through the module.

        :param data: Data to send
        :return: None
        """
        # Example command for data sending (may require configuration for specific platform)
        # This section might need customization depending on the operator and data format.
        try:
            self.at_command.send_command(f'AT+SEND={data}', expected_response="SEND OK")
            print("Data successfully sent")
        except ATCommandError:
            print("Error occurred while sending data")

    def close(self):
        """
        Terminates module usage and closes the UART connection.

        :return: None
        """
        self.at_command.close()
        print("Connection with the module closed")




# from .commands import ATCommand, ATCommandError
#
#
# class SIM7020:
#     """Класс для управления модулем SIM7020 с помощью AT-команд."""
#
#     def __init__(self, port, baudrate=9600, timeout=1):
#         """
#         Инициализация SIM7020 с указанием порта и параметров UART.
#
#         :param port: Порт UART (например, "/dev/ttyUSB0" для Linux)
#         :param baudrate: Скорость передачи данных
#         :param timeout: Таймаут ожидания ответа
#         """
#         self.at_command = ATCommand(port, baudrate, timeout)
#
#     def initialize(self):
#         """
#         Первоначальная настройка модуля: проверка связи и установки начальных параметров.
#
#         :return: None
#         """
#         if not self.at_command.check_connection():
#             raise ATCommandError("Не удалось установить связь с модулем SIM7020")
#
#         print("Модуль SIM7020 успешно подключен")
#
#     def set_apn(self, apn):
#         """
#         Установка APN для подключения к сети.
#
#         :param apn: Название APN
#         :return: None
#         """
#         self.at_command.set_apn(apn)
#         print(f"APN '{apn}' успешно установлен")
#
#     def connect_network(self):
#         """
#         Подключение к сети NB-IoT.
#
#         :return: None
#         """
#         self.at_command.connect_network()
#         print("Подключение к сети выполнено")
#
#     def disconnect_network(self):
#         """
#         Отключение от сети NB-IoT.
#
#         :return: None
#         """
#         self.at_command.disconnect_network()
#         print("Отключение от сети выполнено")
#
#     def get_signal_quality(self):
#         """
#         Получение уровня сигнала от модуля.
#
#         :return: Кортеж (RSSI, BER)
#         """
#         rssi, ber = self.at_command.get_signal_quality()
#         print(f"Уровень сигнала: RSSI={rssi}, BER={ber}")
#         return rssi, ber
#
#     def send_data(self, data):
#         """
#         Отправка данных через модуль.
#
#         :param data: Данные для отправки
#         :return: None
#         """
#         # Пример команды для отправки данных (для настройки на определенной платформе)
#         # Эта часть может потребовать уточнения в зависимости от оператора и формата данных.
#         try:
#             self.at_command.send_command(f'AT+SEND={data}', expected_response="SEND OK")
#             print("Данные успешно отправлены")
#         except ATCommandError:
#             print("Ошибка при отправке данных")
#
#     def close(self):
#         """
#         Завершение работы с модулем, закрытие UART-соединения.
#
#         :return: None
#         """
#         self.at_command.close()
#         print("Соединение с модулем закрыто")
