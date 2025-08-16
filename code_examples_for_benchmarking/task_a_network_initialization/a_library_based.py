# Assumes the library is initialized
from gsm_nbiot_lib import SIM7020
import utime

# Assumes UART_PORT, UART_BAUDRATE, PWR_EN_PIN are defined
# sim7020 = SIM7020(UART_PORT, UART_BAUDRATE, "some_apn", PWR_EN_PIN)

def library_initialize_network(apn):
    try:
        # 1. Power on the module
        sim7020.power_on(PWR_EN_PIN)
        utime.sleep(2)
        
        # 2. Check readiness, set APN, and connect
        sim7020.at.send_command("AT")   # Check readiness
        sim7020.configure_apn()         # CFUN0→APN→CFUN1→CGATT?→CGCONTRDP
        sim7020.connect_network()
        
        print("Network initialization successful.")
        return True
    except Exception as e:
        print(f"Error during network initialization: {e}")
        return False


