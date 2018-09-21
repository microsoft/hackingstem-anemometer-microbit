# ------------__ Hacking STEM – hot_wheels.py – micro:bit __-----------
# For use with the Analyzing Windspeed With Anemometers Lesson plan
# available from Microsoft Education Workshop at
# http://aka.ms/hackingSTEM
#
#  Overview:
#  This project uses:
#    TMP36 temperature sensor input on pin 1
#    Reed switch input on pin 8
#    NPN transistor to control motor voltage output on pin 0
#
#  Each time reed switch is triggered, serial ouput will be a
#  comma delimited line consisting of wind speed (kph), rotations per
#  minute, time interval since last trigger, temperature celsius,
#  temperature Fahrenheit
#  example: TODO
#
#  Input of a comma delimited line with fourth position beaaring a
#  positive integer will spin motor at given rpm
#  example: TODO
#
#  This project uses a BBC micro:bit microcontroller, information at:
#  https://microbit.org/
#
#  Comments, contributions, suggestions, bug reports, and feature
#  requests are welcome! For source code and bug reports see:
#  http://github.com/[TODO github path to Hacking STEM]
#
#  Copyright 2018, Jeremy Franklin-Ross
#  Microsoft EDU Workshop - HackingSTEM
#  MIT License terms detailed in LICENSE.txt
# ===---------------------------------------------------------------===

from microbit import *

REED_SWITCH_PIN = pin8
TMP36_PIN = pin1
NPN_MOTOR_PIN = pin0

# diameter of your anemometer
ANEMOMETER_DIAMETER_INCHES = 9.44

PI = 3.14

# Anemometer circumference in various units
ANEMOMETER_CIRCUMFERENCE_INCHES = ANEMOMETER_DIAMETER_INCHES * PI
ANEMOMETER_CIRCUMFERENCE_FEET = ANEMOMETER_CIRCUMFERENCE_INCHES / 12
ANEMOMETER_CIRCUMFERENCE_MILES = ANEMOMETER_CIRCUMFERENCE_FEET / 5280

# milliseconds per minute (1000 milliseconds * 60 seconds)
MILLIS_PER_MINUTE = 60000

TMD36_OFFSET = 0.5      # Offset defined in tmd26 datasheet
TMD_RESISTOR = 100      # Ohm value of resistor in tmd circuit
ADC_RESOLUTION = 1024   # analoge to digital scale
MICROBIT_VOLTAGE = 3.3  # voltage for circuit calculations


# End of line string
EOL = "\n"

def calc_rpm(time_interval):
    return MILLIS_PER_MINUTE / time_interval

def calc_kph(rpm):
    """ Convert rpm of anemometer to MPH """
    mpm = ANEMOMETER_CIRCUMFERENCE_MILES * rpm    # miles per minute
    mph = mpm * 60        # convert to mph
    kph = mph * 1.609344  # convert to kph
    return kph            # windspeed in kph

def read_temp():
    """ Reads temperature from sensor """
    sensorInput = TMP36_PIN.read_analog()

    # applying ohm's law and circuit parameters to calculate temp in celsius
    temperature_celcius = (((sensorInput / ADC_RESOLUTION) * MICROBIT_VOLTAGE) - TMD36_OFFSET) * TMD_RESISTOR

    return temperature_celcius

def convert_to_fahrenheit(temperature_celcius):
    """ Convert temperature_celcius to Fahrenheit """
    temperature_fahrenheit = temperature_celcius * 9 / 5 + 32

    return temperature_fahrenheit

def set_motor_speed(motor_speed):
    """ sends speed to motor control circuit """
    if motor_speed == 0: display.show(Image.HAPPY)

    analog_speed_value = motor_speed * (5/3.3)
    if analog_speed_value > 1023: analog_speed_value = 1023


    NPN_MOTOR_PIN.write_analog(analog_speed_value)


def process_serial_input():
    """
        gets comma delimited data from serial
        applies changes appropriately

        returns true if reset received
    """
    global gate_switch_count
    built_string = ""
    while uart.any() is True:
        byte_in = uart.read(1)
        if byte_in == b'\n':
            continue
        byte_in = str(byte_in)
        split_byte = byte_in.split("'")
        built_string += split_byte[1]
    if built_string is not "":
        if built_string != "":
            parsed_data = built_string.split(",")
            try:
                speed_str = parsed_data[3]
            except IndexError:
                return

            try:
                if int(speed_str) >= 0:
                    set_motor_speed(int(speed_str))
            except ValueError:
                return

small_heart = False

def toggle_heart():
    """ flips heart display between large and small each time called """
    global small_heart
    if small_heart:
        small_heart = False
        display.show(Image.HEART_SMALL)
    else:
        small_heart = True
        display.show(Image.HEART)



# Set up & config
uart.init(baudrate=9600) # set serial data rate
last_running_time = running_time()
set_motor_speed(0)
display.show(Image.ASLEEP)

#send zeros to begin session
uart.write(EOL+"0,0,0,0,0,0,0,0,0,0,INIT"+EOL)


while True:
    if REED_SWITCH_PIN.read_digital():
        toggle_heart()
        current_running_time = running_time()
        # calculate time interval
        time_interval = current_running_time - last_running_time

        # calculate rpm from interval
        rpm = calc_rpm(time_interval)

        # calculate kph from rpm
        wind_speed = calc_kph(rpm)

        # read temperature from sensor
        temperature_celcius = read_temp()

        # convert to Fahrenheit
        temperature_fahrenheit = convert_to_fahrenheit(temperature_celcius)

        # send the data,
        # format: Wind Speed, Revolutions, Time Interval, temp C, temp F,
        uart.write("{},{},{},{},{},".format(wind_speed,rpm,time_interval,temperature_celcius,temperature_fahrenheit)+EOL)

        # update last_running_time for next passed. ready for next loop!
        last_running_time = current_running_time
        sleep(150) #debounce

    process_serial_input()
