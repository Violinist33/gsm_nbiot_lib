# Assumes sim7020 and config variables are defined
from gsm_nbiot_lib import MQTTClient

def library_mqtt_publish(broker, port, client_id, topic, message):
    try:
        # 1. Initialize the MQTT client
        mqtt_client = MQTTClient(sim7020.at, broker, port, client_id, "")
        
        # 2. Connect to the broker
        mqtt_client.connect()
        
        # 3. Publish the message
        mqtt_client.publish(topic, message)
        
        print("MQTT message published successfully.")
        return True
    except Exception as e:
        print(f"Error during MQTT publish: {e}")
        return False