from ..utils import str_to_hexStr


class MQTTClient:
    """
    A class for working with MQTT via AT commands.

    This class provides methods for connecting, disconnecting, subscribing
    to topics, and publishing messages to an MQTT broker using AT commands.

    Attributes:
        at (object): Interface for sending AT commands.
        broker_address (str): Address of the MQTT broker.
        port (int): Port of the MQTT broker.
        client_id (str): MQTT client identifier.
        device_secret (str): Device secret key for authentication.
    """

    def __init__(self, at_interface, broker_address, port, client_id, device_secret):
        """
        Initializes the MQTTClient.

        Args:
            at_interface (object): Interface for sending AT commands.
            broker_address (str): Address of the MQTT broker.
            port (int): Port of the MQTT broker.
            client_id (str): MQTT client identifier.
            device_secret (str): Device secret key for authentication.
        """
        self.at = at_interface
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.device_secret = device_secret

    def connect(self):
        """
        Connects to the MQTT broker.

        Sends commands to establish a new MQTT connection and authenticate the client.
        """
        print("------------------- mqttConnect -------------------")
        self.at.send_command(f'AT+CMQNEW="{self.broker_address}","{self.port}",12000,1024')
        self.at.send_command(f'AT+CMQCON=0,3,"{self.client_id}",45,1,0,"device","{self.device_secret}"')

    def disconnect(self):
        """
        Disconnects from the MQTT broker.

        Sends a command to terminate the active MQTT connection.
        """
        pass

    def subscribe(self, topic):
        """
        Subscribes to the specified MQTT topic.

        Args:
            topic (str): The topic to subscribe to.
        """
        self.at.send_command(f'AT+CMQSUB=0,"{topic}",1')

    def request_pin_value(self, pin_name):
        """
        Sends a request to retrieve the value of a pin.

        Args:
            pin_name (str): Name of the pin (e.g., "Integer V0", "Voltage").
        """
        topic = "get/ds"  # Topic for requests
        hex_name = str_to_hexStr(pin_name)
        hex_length = len(hex_name)

        command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_name}"'
        self.at.send_command(command)

        # # Wait for response
        # response = self.at.receive_response()
        # return response  # Expecting the device to return the value

    def publish(self, topic, message):
        """
        Publishes a message to the specified MQTT topic.

        The message is converted to a hexadecimal string before sending.

        Args:
            topic (str): The topic to publish the message to.
            message (str): The message to be sent.
        """
        hex_message = str_to_hexStr(message)
        hex_length = len(hex_message)
        command = f'AT+CMQPUB=0,"{topic}",1,0,0,{hex_length},"{hex_message}"'
        return self.at.send_command(command)

    def handle_message(self, topic, message):
        """
        Handles a message received from the MQTT broker.

        Args:
            topic (str): The topic from which the message was received.
            message (str): The message received from the topic.
        """
        pass

    def reconnect(self):
        """
        Attempts to reconnect to the MQTT broker after a connection loss.

        Implements logic for reconnection with exponential backoff.
        """
        pass
