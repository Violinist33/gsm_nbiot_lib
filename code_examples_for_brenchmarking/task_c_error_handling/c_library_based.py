# Assumes sim7020 is initialized
from gsm_nbiot_lib import ATCommandError

def library_error_handling():
    invalid_apn = "invalid.apn"
    
    try:
        # The library encapsulates response validation
        sim7020.configure_apn()
        
        # The connect_network() method will raise an exception on failure
        sim7020.connect_network()
        
        print("Failed to catch expected error.")
        return False
    except ATCommandError as e:
        # The exception is correctly handled
        print(f"Successfully caught network attachment error: {e}")
        return True

from gsm_nbiot_lib import ATCommandError

