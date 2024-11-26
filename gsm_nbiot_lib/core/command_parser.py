# gsm_nbiot_lib/core/command_parser.py

def parse_response(response):
    print("Response: ", response.strip("\r\n"))
    response = response.strip('\r\n')
    lines = response.split('\r\n')
    parts = lines[0].split(': ')
    # parts = response.split(': ', 1)
    command_name = parts[0].strip()
    parameters = []
    if len(parts) > 1:
        parameters = [param.strip().strip('"') for param in parts[1].split(',')]
    return command_name, parameters

