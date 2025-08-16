# Assumes uart is initialized
def manual_error_handling():
    invalid_apn = "invalid.apn"
    
    # Attempt to configure the invalid APN
    cmd = f'AT+CGDCONT=1,"IP","{invalid_apn}"\r\n'
    uart.write(cmd.encode())
    response = uart.read() # This command usually returns OK

    # Attempt to attach to the network, which should fail
    uart.write(b'AT+CGATT=1\r\n')
    # Need to wait for a +CME ERROR or simple ERROR response
    start_time = utime.ticks_ms()
    error_detected = False
    while utime.ticks_diff(utime.ticks_ms(), start_time) < 10000: # 10s timeout
        response = uart.read()
        if response and (b'ERROR' in response or b'+CME ERROR' in response):
            print("Successfully caught network attachment error.")
            error_detected = True
            break
    
    if not error_detected:
        print("Failed to catch expected error.")

    return error_detected