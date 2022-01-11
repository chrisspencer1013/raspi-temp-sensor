#!/usr/bin/env python3

import time
import logging
import colorsys
import os
import sys
import Adafruit_DHT

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

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4


def main():
    try:
        while True:
            humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            logging.info(f"temp: {temp}, humidity: {humidity}")
            time.sleep(3)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()