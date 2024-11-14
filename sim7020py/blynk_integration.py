from .sim7020 import SIM7020
import time
import logging

logging.basicConfig(level=logging.INFO)


class BlynkIntegration:
    """Class for integrating with the Blynk platform using the SIM7020 module."""

    def __init__(self, port: str, apn: str, blynk_token: str, baudrate: int = 9600, timeout: int = 1,
                 max_retries: int = 3):
        """
        Initializes Blynk integration with APN settings and access token.

        Args:
            port (str): UART port for SIM7020 (e.g., "/dev/ttyUSB0" for Linux).
            apn (str): APN name for network connection.
            blynk_token (str): Access token for Blynk.
            baudrate (int): UART connection speed. Defaults to 9600.
            timeout (int): Response timeout. Defaults to 1.
            max_retries (int): Max retries on data send/receive failure. Defaults to 3.
        """
        self.sim7020: SIM7020 = SIM7020(port, baudrate, timeout)
        self.apn: str = apn
        self.blynk_token: str = blynk_token
        self.max_retries: int = max_retries
        self.connected: bool = False  # Tracks connection status

    def connect(self) -> None:
        """
        Connects to the network and initializes a connection with Blynk.
        """
        try:
            self.sim7020.initialize()
            self.sim7020.set_apn(self.apn)
            self.sim7020.connect_network()
            self.connected = True
            logging.info("Connected to network and Blynk")
        except Exception as e:
            logging.error(f"Connection error: {e}")
            self.connected = False

    def ensure_connection(self) -> None:
        """
        Checks the connection and attempts reconnection if needed.
        """
        if not self.connected:
            logging.info("Attempting reconnection...")
            self.connect()

    def send_value(self, virtual_pin: int, value: str) -> None:
        """
        Sends data to a specified virtual pin on Blynk.

        Args:
            virtual_pin (int): Virtual pin number on Blynk.
            value (str): Value to send.
        """
        self.ensure_connection()

        command: str = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/update/{virtual_pin}?value={value}\""
        for attempt in range(self.max_retries):
            try:
                self.sim7020.at_command.send_command(command, expected_response="OK")
                logging.info(f"Value {value} sent to virtual pin {virtual_pin}")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        logging.error(f"Failed to send value to virtual pin {virtual_pin} after {self.max_retries} attempts")

    def get_value(self, virtual_pin: int) -> str | None:
        """
        Retrieves data from a specified virtual pin on Blynk.

        Args:
            virtual_pin (int): Virtual pin number on Blynk.

        Returns:
            str | None: Retrieved value or None on error.
        """
        self.ensure_connection()

        command: str = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/get/{virtual_pin}\""
        for attempt in range(self.max_retries):
            try:
                response: list[str] = self.sim7020.at_command.send_command(command, expected_response="OK")
                data: str = response[-1].split()[-1]  # Example response parsing
                logging.info(f"Retrieved value {data} from virtual pin {virtual_pin}")
                return data
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        logging.error(f"Failed to retrieve data from virtual pin {virtual_pin} after {self.max_retries} attempts")
        return None

    def disconnect(self) -> None:
        """
        Disconnects from Blynk and the NB-IoT network.
        """
        self.sim7020.disconnect_network()
        self.connected = False
        logging.info("Disconnected from Blynk and NB-IoT network")

    def close(self) -> None:
        """
        Closes the connection with the SIM7020 module.
        """
        self.sim7020.close()
        logging.info("Closed connection with SIM7020")
