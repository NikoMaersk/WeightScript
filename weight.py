import RPi.GPIO as GPIO
from hx711 import HX711

try:
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=13, pd_sck_pin=6)
    print(" please don't place anything on the weigth")
    hx.zero() #reset the hx711
    initial_reading = hx.get_raw_data_mean() #get value without weight
    input("Put a known weight on the weight and press enter")
    cali_reading =hx.get_data_mean()
    known_weight = input("How much weight did you put on in gr")
    hx.set_scale_ratio(cali_reading/float(known_weight)) #set the ratio to the value change for each gram
    input ("calibration done, press Enter to read weight values")
    while True:
       print(hx.get_weight_mean(20), "g") # print the value in gram
finally:
    GPIO.cleanup()
