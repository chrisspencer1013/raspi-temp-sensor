#!/usr/bin/env python3

import time
import logging
import colorsys
import os
import sys
import ST7735

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559

    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from subprocess import PIPE, Popen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("""initializing...""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
path = os.path.dirname(os.path.realpath(__file__))
font_size = 20
font = ImageFont.truetype(UserFont, font_size)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index("=") + 1 : output.rindex("'")])


CPU_TEMPS = [get_cpu_temperature()] * 5


def get_adjusted_room_temp():
    # Tuning factor for compensation. Decrease this number to adjust the
    # temperature down, and increase to adjust up
    factor = 2.25

    cpu_temp = get_cpu_temperature()

    # Smooth out with some averaging to decrease jitter
    nonlocal CPU_TEMPS
    CPU_TEMPS = CPU_TEMPS[1:] + [CPU_TEMPS]
    avg_cpu_temp = sum(CPU_TEMPS) / float(len(CPU_TEMPS))

    raw_temp = bme280.get_temperature()

    adjusted_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

    # return in F
    return adjusted_temp * 1.8 + 32


def update_display(temp, humidity):
    draw.text((0, 0), f"Temp: {temp}°F", font=font, fill=(0, 45, 255))
    draw.text((0, 25), f"Humidity: {humidity}% ", font=font, fill=(0, 45, 255))
    st7735.display(img)


def main():
    try:
        while True:
            temp = get_adjusted_room_temp()
            humidity = bme280.get_humidity()
            update_display(temp, humidity)
            logging.info(f"temp: {temp}, humidity: {humidity}")
            time.sleep(3)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()