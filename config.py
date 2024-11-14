from decouple import config

APN: str = config("APN", default='nbiot', cast=str)
BLYNK_TOKEN: str = config("BLYNK_TOKEN", cast=str)
BROKER_ADDRESS: str = config("BROKER_ADDRESS", default='blynk.cloud', cast=str)
DEVICE_NAME: str = config("DEVICE_NAME", cast=str)
DEVICE_SECRET: str = config("DEVICE_SECRET", cast=str)