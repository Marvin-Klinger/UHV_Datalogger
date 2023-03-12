import serial
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from pymeasure.instruments.keithley import Keithley2000
import numpy as np
import matplotlib.animation as animation

time_at_beginning_of_experiment = datetime.now()


def gettemperature():
    with Keithley2000("ASRL/dev/ttyS2::INSTR") as meter:
        #meter.measure_resistance(max_resistance=1000.0, wires=2)
        resistance = float(meter.resistance)

    temperature = (-100 * 0.0039083 + np.sqrt(
        100 * 100 * 0.0039083 * 0.0039083 - 4 * 100 * (-0.0000005775) * (100 - resistance))) / (
                          2 * 100 * (-0.0000005775))
    return temperature


def getpressure():
    with serial.Serial('/dev/ttyS3', 9600, timeout=5) as ser:
        ser_line = ser.readline()
    ser_line = str(ser_line)
    content = ser_line.split(',')
    pressure = float(content[1])
    return pressure


def data_gen():
    cnt = 0
    while cnt < 1000:
        timedelta = datetime.now() - time_at_beginning_of_experiment
        time = timedelta.total_seconds()
        while True:
            try:
                y1 = gettemperature()
                y2 = getpressure()
                lgr.info(str(time) + ';' + str(y2) + ';' + str(y1))
                break
            except:
                print("Error during data aquisition, retrying...")
                continue
        yield time, y1, y2


with Keithley2000("ASRL/dev/ttyS2::INSTR") as meter:
    meter.measure_resistance(max_resistance=1000.0, wires=2)
    float(meter.resistance)

# create logger
lgr = logging.getLogger('outgassing')
lgr.setLevel(logging.DEBUG)
# log all escalated at and above DEBUG

fh = logging.FileHandler('./'+ str(time_at_beginning_of_experiment) +'outgassing_DyAg_130CLangeStandzeitVorhere.csv')
fh.setLevel(logging.DEBUG)

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
lgr.addHandler(fh)

# create a figure with two subplots
#fig, (ax1, ax2) = plt.subplots(2,1)
fig, ax1 = plt.subplots(1,1)
ax2 = ax1.twinx()

# intialize two line objects (one in each axes)
line1, = ax1.plot([], [], color='r')
line2, = ax2.plot([], [], color='b')
line = [line1, line2]

# the same axes initalizations as before (just now we do it for both of them)
ax1.set_ylim(10, 200)
ax1.set_xlim(0, 5)

ax2.set_ylim(1E-9, 5E-1)
ax2.set_yscale('log')
ax2.set_xlim(0, 5)
ax2.grid()

ax2.set_xlabel('Zeit', fontsize=10)
ax2.set_ylabel('Druck (mbar)', fontsize=10)

ax1.set_xlabel('Zeit', fontsize=10)
ax1.set_ylabel('Temperatur (°C)', fontsize=10)

# initialize the data arrays
xdata, y1data, y2data = [], [], []


def run(data):
    # update the data
    t, y1, y2 = data
    xdata.append(t)
    y1data.append(y1)
    y2data.append(y2)

    # axis limits checking. Same as before, just for both axes
    for ax in [ax1, ax2]:
        xmin, xmax = ax.get_xlim()
        if t >= xmax:
            ax.set_xlim(xmin, xmax+5)
            ax.figure.canvas.draw()

    # update the data of both line objects
    line[0].set_data(xdata, y1data)
    line[1].set_data(xdata, y2data)

    fig.suptitle(
        'Outgassing Test, p = ' + str(y2) + 'mbar, T = ' + str(round(y1, 2)) + '°C, Δt = ' + str(
            datetime.now() - time_at_beginning_of_experiment))

    return line


ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=10,
    repeat=False)

plt.show()