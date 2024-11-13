from .commands import ATCommand, ATCommandError


class SIM7020:
    """Класс для управления модулем SIM7020 с помощью AT-команд."""

    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Инициализация SIM7020 с указанием порта и параметров UART.

        :param port: Порт UART (например, "/dev/ttyUSB0" для Linux)
        :param baudrate: Скорость передачи данных
        :param timeout: Таймаут ожидания ответа
        """
        self.at_command = ATCommand(port, baudrate, timeout)

    def initialize(self):
        """
        Первоначальная настройка модуля: проверка связи и установки начальных параметров.

        :return: None
        """
        if not self.at_command.check_connection():
            raise ATCommandError("Не удалось установить связь с модулем SIM7020")

        print("Модуль SIM7020 успешно подключен")

    def set_apn(self, apn):
        """
        Установка APN для подключения к сети.

        :param apn: Название APN
        :return: None
        """
        self.at_command.set_apn(apn)
        print(f"APN '{apn}' успешно установлен")

    def connect_network(self):
        """
        Подключение к сети NB-IoT.

        :return: None
        """
        self.at_command.connect_network()
        print("Подключение к сети выполнено")

    def disconnect_network(self):
        """
        Отключение от сети NB-IoT.

        :return: None
        """
        self.at_command.disconnect_network()
        print("Отключение от сети выполнено")

    def get_signal_quality(self):
        """
        Получение уровня сигнала от модуля.

        :return: Кортеж (RSSI, BER)
        """
        rssi, ber = self.at_command.get_signal_quality()
        print(f"Уровень сигнала: RSSI={rssi}, BER={ber}")
        return rssi, ber

    def send_data(self, data):
        """
        Отправка данных через модуль.

        :param data: Данные для отправки
        :return: None
        """
        # Пример команды для отправки данных (для настройки на определенной платформе)
        # Эта часть может потребовать уточнения в зависимости от оператора и формата данных.
        try:
            self.at_command.send_command(f'AT+SEND={data}', expected_response="SEND OK")
            print("Данные успешно отправлены")
        except ATCommandError:
            print("Ошибка при отправке данных")

    def close(self):
        """
        Завершение работы с модулем, закрытие UART-соединения.

        :return: None
        """
        self.at_command.close()
        print("Соединение с модулем закрыто")
