# gsm_nbiot_lib/integrations/mqtt.py

from gsm_nbiot_lib.utils.helpers import str_to_hexStr


class MQTTClient:
    """
    Клас для роботи з MQTT через AT-команди.

    Цей клас надає методи для підключення, відключення, підписки
    на топіки та публікації повідомлень у MQTT-брокері за допомогою AT-команд.

    Атрибути:
        at (object): Інтерфейс для відправлення AT-команд.
        broker_address (str): Адреса MQTT-брокера.
        port (int): Порт MQTT-брокера.
        client_id (str): Ідентифікатор клієнта MQTT.
        device_secret (str): Секретний ключ пристрою для автентифікації.
    """

    def __init__(self, at_interface, broker_address, port, client_id, device_secret):
        """
        Ініціалізує MQTTClient.

        Args:
            at_interface (object): Інтерфейс для відправлення AT-команд.
            broker_address (str): Адреса MQTT-брокера.
            port (int): Порт MQTT-брокера.
            client_id (str): Ідентифікатор клієнта MQTT.
            device_secret (str): Секретний ключ пристрою для автентифікації.
        """
        self.at = at_interface
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.device_secret = device_secret

    def connect(self):
        """
        Підключається до MQTT-брокера.

        Відправляє команди для створення нового MQTT-з'єднання та автентифікації клієнта.
        """
        print("------------------- mqttConnect -------------------")
        self.at.send_command(f'AT+CMQNEW="{self.broker_address}","{self.port}",12000,1024')
        self.at.send_command(f'AT+CMQCON=0,3,"{self.client_id}",45,1,0,"device","{self.device_secret}"')

    def disconnect(self):
        """
        Відключається від MQTT-брокера.

        Відправляє команду для завершення активного MQTT-з'єднання.
        """
        self.at.sendCMD_waitRespLine("AT+CMQDISCON=0", 1, False)

    def subscribe(self, topic):
        """
        Підписується на вказаний топік MQTT.

        Args:
            topic (str): Топік, на який потрібно підписатися.
        """
        self.at.send_command(f'AT+CMQSUB=0,"{topic}",1')

    def request_pin_value(self, pin_name):
        """
        Надсилає запит на отримання значення пина.

        Args:
            pin_name (str): Назва пина (наприклад, "Integer V0", "Voltage").
        """
        topic = "get/ds"  # Топік для запитів
        hex_name = str_to_hexStr(pin_name)
        hex_length = len(hex_name)

        command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_name}"'
        self.at.send_command(command)

        # # Очікувати відповідь
        # response = self.at.receive_response()
        # return response  # Очікуємо, що пристрій поверне значення

    def publish(self, topic, message):
        """
        Публікує повідомлення у вказаний топік MQTT.

        Повідомлення конвертується у шістнадцятковий рядок перед відправленням.

        Args:
            topic (str): Топік, до якого надсилається повідомлення.
            message (str): Повідомлення, яке потрібно надіслати.
        """
        hex_message = str_to_hexStr(message)
        hex_length = len(hex_message)
        command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_message}"'
        self.at.send_command(command)

