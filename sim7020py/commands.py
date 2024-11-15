import time
from machine import UART


class ATCommandError(Exception):
    """Exception for AT command errors."""
    pass


class ATCommand:
    """Class for sending and handling AT commands for the SIM7020 module via UART."""

    def __init__(self, uart: UART, baudrate: int = 9600, timeout: int = 1):
        """
        Initializes a connection with the module via UART.

        Args:
            uart (UART): UART instance from the machine module.
            baudrate (int, optional): Data transfer rate. Defaults to 9600.
            timeout (int, optional): Timeout for response waiting in seconds. Defaults to 1.
        """
        self.uart = uart
        self.baudrate = baudrate
        self.timeout = timeout
        self.uart.init(baudrate=self.baudrate, timeout=self.timeout)

    def send_command(self, command: str, expected_response: str = "OK", delay: float = 0.5) -> list[str]:
        """
        Sends an AT command and waits for a response.

        Args:
            command (str): AT command to send.
            expected_response (str, optional): Expected response. Defaults to "OK".
            delay (float, optional): Delay before reading the response in seconds. Defaults to 0.5.

        Returns:
            list[str]: Response from the module.

        Raises:
            ATCommandError: If the expected response is not received.
        """
        self.uart.write((command + "\r\n").encode())  # Send the command
        time.sleep(delay)  # Wait for the response

        response = b""
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < self.timeout * 1000:
            if self.uart.any():  # Check if data is available
                data = self.uart.read(self.uart.any())
                response += data
                print(f"Received data: {data}")  # Print received data

        response_lines = response.decode().splitlines()
        print(f"Parsed response lines: {response_lines}")  # Print parsed response lines

        if expected_response not in response_lines:
            raise ATCommandError(f"Expected response '{expected_response}' not received")

        return response_lines

    def check_connection(self) -> bool:
        """
        Checks the connection with the module using the AT command.

        Returns:
            bool: True if the module responds, False otherwise.
        """
        try:
            response = self.send_command("AT")
            return "OK" in response
        except ATCommandError:
            return False

    def get_signal_quality(self) -> tuple[int, int]:
        """
        Requests the signal quality from the module (AT+CSQ command).

        Returns:
            tuple[int, int]: Signal quality (RSSI and BER).

        Raises:
            ATCommandError: If signal quality cannot be retrieved.
        """
        response = self.send_command("AT+CSQ")

        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = map(int, signal_info.split(","))
                return rssi, ber

        raise ATCommandError("Failed to retrieve signal quality")

    def set_apn(self, apn: str) -> None:
        """
        Sets the APN (Access Point Name) for network connection.

        Args:
            apn (str): The APN name.
        """
        self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')

    def connect_network(self) -> None:
        """
        Connects to the network (AT+CGATT=1 command).
        """
        self.send_command("AT+CGATT=1")

    def disconnect_network(self) -> None:
        """
        Disconnects from the network (AT+CGATT=0 command).
        """
        self.send_command("AT+CGATT=0")

    def close(self) -> None:
        """
        Closes the UART connection.
        """
        self.uart.deinit()  # Deinitialize UART
