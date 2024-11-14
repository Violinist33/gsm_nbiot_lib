import time
import serial  # Library for UART communication

class ATCommandError(Exception):
    """Exception for AT command errors."""
    pass

class ATCommand:
    """Class for sending and handling AT commands for the SIM7020 module via UART."""

    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 1):
        """
        Initializes the connection with the module via UART.

        Args:
            port (str): UART port (e.g., "/dev/ttyUSB0" for Linux).
            baudrate (int, optional): Data transmission speed. Defaults to 9600.
            timeout (int, optional): Response timeout. Defaults to 1.
        """
        # Serial instance for UART communication setup
        self.serial: serial.Serial = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, command: str, expected_response: str = "OK", delay: float = 0.5) -> list[str]:
        """
        Sends an AT command and waits for a response.

        Args:
            command (str): AT command to send.
            expected_response (str, optional): Expected response. Defaults to "OK".
            delay (float, optional): Delay before reading the response. Defaults to 0.5 seconds.

        Returns:
            list[str]: Response from the module.

        Raises:
            ATCommandError: If the expected response is not received.
        """
        # Clears the buffer and sends the command
        self.serial.reset_input_buffer()
        self.serial.write((command + "\r\n").encode())

        # Delay to ensure module has time to respond
        time.sleep(delay)
        # Readlines to capture response, and decode bytes to string format
        response: list[str] = [line.decode().strip() for line in self.serial.readlines()]

        # Checks for the presence of the expected response
        if expected_response not in response:
            raise ATCommandError(f"Expected response '{expected_response}' not received")

        return response

    def check_connection(self) -> bool:
        """
        Checks connection with the module using the AT command.

        Returns:
            bool: True if the module responds, otherwise False.
        """
        try:
            response: list[str] = self.send_command("AT")
            return "OK" in response
        except ATCommandError:
            return False

    def get_signal_quality(self) -> tuple[int, int]:
        """
        Requests signal quality from the module (AT+CSQ command).

        Returns:
            tuple[int, int]: Signal quality (RSSI and BER).

        Raises:
            ATCommandError: If signal quality could not be obtained.
        """
        response: list[str] = self.send_command("AT+CSQ")

        # Expected format: "+CSQ: <rssi>,<ber>"
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi: int  # Received Signal Strength Indicator
                ber: int  # Bit Error Rate
                rssi, ber = map(int, signal_info.split(","))
                return rssi, ber

        raise ATCommandError("Signal quality could not be obtained")

    def set_apn(self, apn: str) -> None:
        """
        Sets the APN (Access Point Name) for network connection.

        Args:
            apn (str): APN name.
        """
        # Sends command to set APN
        self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')

    def connect_network(self) -> None:
        """
        Connects to the network (AT+CGATT=1 command).
        """
        # Sends network connection command
        self.send_command("AT+CGATT=1")

    def disconnect_network(self) -> None:
        """
        Disconnects from the network (AT+CGATT=0 command).
        """
        # Sends network disconnection command
        self.send_command("AT+CGATT=0")

    def close(self) -> None:
        """
        Closes the UART connection.
        """
        # Closes the serial communication
        self.serial.close()
