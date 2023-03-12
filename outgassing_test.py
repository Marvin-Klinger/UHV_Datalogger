import serial
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from pymeasure.instruments.keithley import Keithley2000
import numpy as np
import matplotlib.animation as animation


timestamps = []
data_temp = []
data_press = []
lines = []

time_at_beginning_of_experiment = datetime.now()

#meter = Keithley2000("ASRL/dev/ttyS2::INSTR", baud_rate=9600)
#meter.measure_resistance(max_resistance=1000.0, wires=2)

def getTemperature():
    with Keithley2000("ASRL/dev/ttyS2::INSTR") as meter:
        meter.measure_resistance(max_resistance=1000.0, wires=2)
        resistance = float(meter.resistance)

    temperature = (-100 * 0.0039083 + np.sqrt(
        100 * 100 * 0.0039083 * 0.0039083 - 4 * 100 * (-0.0000005775) * (100 - resistance))) / (
                          2 * 100 * (-0.0000005775))
    return temperature

def getPressure():
    with serial.Serial('/dev/ttyS3', 9600, timeout=5) as ser:
        ser_line = ser.readline()
    ser_line = str(ser_line)
    content = ser_line.split(',')
    pressure = float(content[1])
    return pressure


plt.ion()

fig, subplots = plt.subplots(2)
fig.suptitle('Outgassing Test')
plt.show()

# create logger
lgr = logging.getLogger('outgassing')
lgr.setLevel(logging.DEBUG) # log all escalated at and above DEBUG

fh = logging.FileHandler('./'+ str(time_at_beginning_of_experiment) +'outgassing.csv')
fh.setLevel(logging.DEBUG)

# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(message)s')
fh.setFormatter(frmt)

# add the Handler to the logger
lgr.addHandler(fh)


pressure = 1000
temperature = 22

subplots[0].clear()
subplots[0].set_yscale('log')
#    subplots[0].plot(timestamps, data_press, color = 'blue')
subplots[0].set_xlabel('Zeit', fontsize=10)
subplots[0].set_ylabel('Druck (mbar)', fontsize=10)

subplots[1].clear()
subplots[1].set_xlabel('Zeit', fontsize=10)
subplots[1].set_ylabel('Temperatur (°C)', fontsize=10)
#    subplots[1].plot(timestamps, data_temp, color = 'red')

timestamps.append(0)
data_temp.append(20)
data_press.append(1000)

for subplot in subplots:
    line, = subplot.plot(timestamps, data_press)
    lines.append(line)

plt.show()


#    fig.canvas.draw()
#    fig.canvas.flush_events()

def animate(i):
    try:
        i_pressure = getPressure()
        i_temperature = getTemperature()

    except NameError:
        # List from gauge could not be split right -> sometimes happens when entering a new range
        print("IndexError!")

    else:
        # no error
        data_press.append(i_pressure)
        data_temp.append(i_temperature)
        timedelta = datetime.now() - time_at_beginning_of_experiment
        timestamps.append(timedelta.total_seconds())
        lgr.info(str(timedelta.total_seconds()) + ';' + str(i_pressure) + ';' + str(i_temperature))

        fig.suptitle(
            'Outgassing Test, p = ' + str(i_pressure) + 'mbar, T = ' + str(round(i_temperature, 2)) + '°C, Δt = ' + str(
                datetime.now() - time_at_beginning_of_experiment))

        lines[0].set_ydata(data_press)
        lines[0].set_xdata(timestamps)

        lines[1].set_ydata(data_temp)
        lines[1].set_xdata(timestamps)

        plt.title("p_min = " + str(min(data_press)))

        lines[0].figure.canvas.draw()
        lines[1].figure.canvas.draw()
    return lines,

ani = animation.FuncAnimation(fig, animate, interval=1000, blit=True)

plt.show()
