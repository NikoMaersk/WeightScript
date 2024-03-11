import RPi.GPIO as GPIO
from hx711 import HX711
from datetime import datetime
from websocket import create_connection
import json


def init():
    GPIO.setmode(GPIO.BCM)


def get_date_and_time():
    now = datetime.now()
    global dt_string
    return now.strftime("%d/%m/%Y %H:%M:%S")


def connect():
    global ws
    ws = create_connection("ws://10.176.69.180:7070")
    print("Connection established")


def measure_weight():
    try:
        hx = HX711(dout_pin = 13, pd_sck_pin = 6)
        print("Please don't place anything on the weight.")
        hx.zero() # Reset the hx711
        initial_reading = hx.get_raw_data_mean() # Get value without weight
        input("Put a known weight on the weight and press enter.")
        cali_reading = hx.get_data_mean()
        known_weight = input("How much weight did you put on in gram? ")
        hx.set_scale_ratio(cali_reading/float(known_weight)) # Set the ratio to the value change for each gram
        input ("Calibration done, press Enter to read weight values.")
        while True:
            weight = hx.get_weight_mean(20)
            print(weight, "g") # Print the value in gram
            message = { "date":f"{get_date_and_time()}", "weight":f"{weight}" }
            json_as_string = json.dumps(message)
            print(json_as_string)
            ws.send(json_as_string)
    finally:
        GPIO.cleanup()


def main():
    init()
    connect()
    measure_weight()


if __name__ == "__main__":
    main()