# gsm_nbiot_lib/core/at_command.py

import utime
from machine import UART
from gsm_nbiot_lib.core.command_parser import parse_response
from gsm_nbiot_lib.core.errors import ATCommandError
from gsm_nbiot_lib.utils.helpers import sleep_fn


class ATCommandInterface:
    def __init__(self, uart_port=0, baudrate=115200, timeout=5000):
        self.uart = UART(uart_port, baudrate=baudrate, bits=8, parity=None, stop=1)
        self.timeout = timeout

    def send_command(self, cmd, attempts=5, sleep_on_error=True):
        response = ""
        for attempt in range(attempts):
            print(f"Attempt {attempt + 1}: Sending command: {cmd}")
            self.uart.write((cmd + '\r\n').encode())
            response = self.wait_response_line()
            if response and response not in ["ERROR", "TIMEOUT"]:
                break
            utime.sleep(1)

        if sleep_on_error and response in ["ERROR", "TIMEOUT"]:
            sleep_fn(0.1)
            raise ATCommandError(f"Command '{cmd}' failed with response: {response}")

        command_name, parameters = parse_response(response)
        return command_name, parameters

    def wait_response_line(self):
        response = ""
        start_time = utime.ticks_ms()
        while (utime.ticks_ms() - start_time) < self.timeout:
            if self.uart.any():
                char = self.uart.read(1).decode()
                response += char
                if response.endswith("OK\r\n") or response.endswith("ERROR\r\n") or response.endswith("TIMEOUT\r\n"):
                    break
        if response.endswith("OK\r\n"):
            return response
        elif response.endswith("ERROR\r\n"):
            return "ERROR"
        elif response.endswith("TIMEOUT\r\n") or not response:
            return "TIMEOUT"
        return response
