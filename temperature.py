from pymeasure.instruments.keithley import Keithley2000
import serial
import numpy as np
from pymeasure.adapters import SerialAdapter
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
lgr = logging.getLogger('temperatur')
lgr.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
# add a file handler
fh = logging.FileHandler('./temperature.csv')
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
lgr.addHandler(fh)

meter = Keithley2000("ASRL/dev/ttyS2::INSTR", baud_rate=9600)
#meter = Keithley2000('ASRL3::INSTR')
meter.measure_resistance(max_resistance=1000.0, wires=2)

print(meter.resistance)
print(meter.resistance)
while(1):
    resistance = float(meter.resistance)
    temperature = (-100*0.0039083 + np.sqrt(100*100*0.0039083*0.0039083 - 4*100*(-0.0000005775)*(100-resistance)))/(2*100*(-0.0000005775))
    lgr.info(temperature)
    data.append(temperature)
    timestamps.append(datetime.now())
    ax.clear()
    ax.set_xlabel('Zeit', fontsize=10)
    ax.set_ylabel('Temperatur (°C)', fontsize=10)
    ax.set_title('Aktuell: T = ' + str(round(temperature, 2)) + '°C', fontsize=10)

    ax.plot(timestamps, data)
    fig.canvas.draw()
    fig.canvas.flush_events()