from gsm_nbiot_lib.core.at_command import ATCommandInterface
from gsm_nbiot_lib.core.errors import ConnectionError
from machine import Pin

class ConnectionManager:
    def __init__(self, at_interface: ATCommandInterface, apn: str):
        self.at = at_interface
        self.apn = apn
        self.signal_quality = 0
        self.lampIsOn = 1

    def power_on(self, pwr_en_pin):
        pwr_key = Pin(pwr_en_pin, Pin.OUT)
        pwr_key.value(1)

    def power_off(self, pwr_en_pin):
        pwr_key = Pin(pwr_en_pin, Pin.OUT)
        pwr_key.value(0)

    def configure_apn(self):
        self.at.send_command("AT+CFUN=0")
        self.at.send_command(f'AT*MCGDEFCONT="IP","{self.apn}"')
        self.at.send_command("AT+CFUN=1")
        self.at.send_command("AT+CGATT?")
        self.at.send_command("AT+CGCONTRDP")

    def check_signal_quality(self):
        cmd, params = self.at.send_command("AT+CSQ")
        if cmd == "+CSQ" and params:
            self.signal_quality = int(params[0])
