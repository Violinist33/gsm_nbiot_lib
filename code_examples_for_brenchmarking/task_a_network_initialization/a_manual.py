# Assumes uart and pwr_key are already initialized
import utime
from machine import UART, Pin

# uart = UART(0, baudrate=115200, timeout=5000)
# pwr_key = Pin(14, Pin.OUT)

def manual_initialize_network(apn):
    # 1. Power on the module
    pwr_key.value(1)
    utime.sleep(2)
    
    # 2. Check if the module is ready (expect "OK")
    for _ in range(3):
        uart.write(b'AT\r\n')
        response = uart.read()
        if response and b'OK' in response:
            print("Module is ready.")
            break
        utime.sleep(1)
    else:
        print("Error: Module not responding.")
        return False

    # 3. Enable full functionality
    uart.write(b'AT+CFUN=1\r\n')
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to set CFUN=1.")
        return False
    utime.sleep(1)

    # 4. Configure APN
    cmd = f'AT+CGDCONT=1,"IP","{apn}"\r\n'
    uart.write(cmd.encode())
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to set APN.")
        return False

    # 5. Attach to the network
    uart.write(b'AT+CGATT=1\r\n')
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to attach to network.")
        return False
        
    print("Network initialization successful.")
    return True