import serial

import logging
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np



timestamps = []
data = []

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)


# create logger
lgr = logging.getLogger('druck')
lgr.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
# add a file handler
fh = logging.FileHandler('./pressure.csv')
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
lgr.addHandler(fh)
while(1):
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=20) as ser:
        line = ser.readline()
    line = str(line)
    list = line.split(',')
    pressure = float(list[1])
    # You can now start issuing logging statements in your code
    lgr.info(pressure)
    data.append(pressure)
    timestamps.append(datetime.now())
    ax.clear()
    ax.set_yscale('log')
    ax.plot(timestamps, data)
    ax.set_title('Aktuell: p = ' + str(pressure) + 'mbar', fontsize=10)
    fig.canvas.draw()
    fig.canvas.flush_events()