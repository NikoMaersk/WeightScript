import RPi.GPIO as GPIO
from hx711 import HX711
from datetime import datetime
from websocket import create_connection
import time
import json


CURRENT_WEIGHT = 0

def init():
    global LED
    global TRIG
    global ECHO
    global CURRENT_WEIGHT
    global PREVIOUS_WEIGHT
    CURRENT_WEIGHT = 0
    PREVIOUS_WEIGHT = 0
    LED = 16
    TRIG = 20
    ECHO = 21

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(LED, False)


def get_date_and_time():
    now = datetime.now()
    global dt_string
    return now.strftime("%d/%m/%Y %H:%M:%S")


def get_distance():
    LIMIT = 5
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time() 
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance < LIMIT
    

def connect():
    global ws
    ws = create_connection("ws://10.176.69.178:7070")
    print("Connection established")


def measure_weight():
    global CURRENT_WEIGHT
    global PREVIOUS_WEIGHT
    try:
        hx = HX711(dout_pin=6, pd_sck_pin=5)
        print("Please don't place anything on the weight.")
        hx.zero()  # Reset the hx711
        initial_reading = hx.get_raw_data_mean()  # Get value without weight
        input("Put a known weight on the weight and press enter.")
        cali_reading = hx.get_data_mean()
        known_weight = input("How much weight did you put on in gram? ")
        hx.set_scale_ratio(cali_reading / float(known_weight))  # Set the ratio to the value change for each gram
        input("Calibration done, press Enter to read weight values.")
        while True:
            weight = hx.get_weight_mean(20)
            print(weight, "g")  # Print the value in grams
            
            if CURRENT_WEIGHT > PREVIOUS_WEIGHT:
                message = {"date": f"{get_date_and_time()}", "weight": f"{CURRENT_WEIGHT}"}
                json_as_string = json.dumps(message)
                print("Sending data: " + json_as_string)
                ws.send(json_as_string)
                if get_distance():
                    GPIO.output(LED, True)

            PREVIOUS_WEIGHT = CURRENT_WEIGHT
            CURRENT_WEIGHT += weight
            time.sleep(1)

    finally:
        GPIO.cleanup()


def main():
    init()
    connect()
    measure_weight()


if __name__ == "__main__":
    main()