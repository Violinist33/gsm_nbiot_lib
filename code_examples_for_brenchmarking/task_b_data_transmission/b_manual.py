# Assumes uart is initialized and network is available
def manual_mqtt_publish(broker, port, client_id, topic, message):
    # 1. Configure the MQTT broker connection
    cmd_new = f'AT+CMQNEW="{broker}","{port}",12000,1024\r\n'
    uart.write(cmd_new.encode())
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to create MQTT connection.")
        return False
    utime.sleep(1)

    # 2. Connect to the broker
    cmd_con = f'AT+CMQCON=0,3,"{client_id}",600,0,0\r\n'
    uart.write(cmd_con.encode())
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to connect to MQTT broker.")
        return False
    utime.sleep(2)

    # 3. Publish the message
    hex_message = message.encode().hex()
    msg_len = len(hex_message)
    cmd_pub = f'AT+CMQPUB=0,"{topic}",1,0,0,{msg_len},"{hex_message}"\r\n'
    uart.write(cmd_pub.encode())
    response = uart.read()
    if not (response and b'OK' in response):
        print("Error: Failed to publish message.")
        return False
        
    print("MQTT message published successfully.")
    return True