# gsm_nbiot_lib/modules/sim7020.py

from gsm_nbiot_lib.core.connection import ConnectionManager
from gsm_nbiot_lib.core.at_command import ATCommandInterface
from gsm_nbiot_lib.utils.helpers import save_state, load_state

class SIM7020(ConnectionManager):
    def __init__(self, uart_port, baudrate, apn, pwr_en_pin):
        at_interface = ATCommandInterface(uart_port, baudrate)
        super().__init__(at_interface, apn)
        self.pwr_en_pin = pwr_en_pin
        self.load_lamp_state()

    def load_lamp_state(self):
        loaded_state = load_state('state.db')
        self.lampIsOn = int(loaded_state) if loaded_state else 1

    def save_lamp_state(self):
        save_state('state.db', self.lampIsOn)

    def toggle_lamp(self):
        self.lampIsOn = 1 if self.lampIsOn == 0 else 0
        self.save_lamp_state()
        # Тут можна додати код для керування світлодіодами
