import matplotlib.pyplot as plt
from io import TextIOWrapper
from typing import Tuple
import numpy as np
from scipy.interpolate import splrep, splev


def readdata(file: TextIOWrapper, timestep: float = 1/1000, delay: int = 0) -> np.ndarray:
    
    file.seek(0)
    lines = file.readlines()
    data = np.empty((len(lines)-delay, 4), float)
    for i in range(len(lines)-delay):
        command = float(lines[i].strip().split('\t')[0])/100
        measure = -float(lines[i+delay].strip().split('\t')[1])/10**6
        if not i:
            c0 = command
            m0 = measure
        data[i, 0] = i*timestep
        data[i, 1] = command-c0
        data[i, 2] = measure-m0
        data[i, 3] = abs((command-c0)-(measure-m0))
    return data


def filtedif(data: np.ndarray, maxdif: float = 10, both=False) -> np.ndarray:
    res = np.copy(data)
    for row in res:
        if row[3] > maxdif:
            if both:
                row[1] = np.nan
            row[2] = np.nan
            row[3] = np.nan
    return res


def filternan(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    resx = []
    resy = []
    if x.size == y.size:
        for i in range(x.size):
            if not (np.isnan(x[i]) or np.isnan(y[i])):
                resx.append(x[i])
                resy.append(y[i])
    else:
        raise Exception('Array sizes must be equal!')
    return np.asarray(resx), np.asarray(resy)


def splinesmooth(data: np.ndarray, smootness: float, der: int = 0, mult: float = 1) -> np.ndarray:
    res = np.empty_like(data)
    res[:, 0] = data[:, 0]
    for i in range(1, 3):
        spl = splrep(*filternan(data[:, 0], data[:, i]), s=smootness)
        res[:, i] = np.multiply(splev(data[:, 0], spl, der=der), mult)
    res[:, 3] = np.abs(np.subtract(res[:, 1], res[:, 2]))
    return res


def plotdata3(file: TextIOWrapper):
    data = readdata(file, delay=4, timestep=1/1000)
    filtered = filtedif(data, maxdif=2)
    smoothed = splinesmooth(filtered, 0.01)
    vel = splinesmooth(filtered, 0.01, 1, 1/1000)
    acc = splinesmooth(vel, 0.01, 1)

    axs = plt.subplots(4, sharex=True)[1]

    axs[0].plot(smoothed[:, 0], smoothed[:, 1], label='command')
    axs[0].plot(smoothed[:, 0], smoothed[:, 2], label='measurement')
    axs[3].plot(smoothed[:, 0], smoothed[:, 3])
    axs[1].plot(smoothed[:, 0], vel[:, 1], label='command')
    axs[1].plot(smoothed[:, 0], vel[:, 2], label='measurement')
    axs[2].plot(smoothed[:, 0], acc[:, 1], label='command')
    axs[2].plot(smoothed[:, 0], acc[:, 2], label='measurement')

    axs[0].set(ylabel='mm')
    axs[0].set_title('Position', loc='left', pad=-17, y=1, x=0.005)
    axs[1].set(ylabel='m/s')
    axs[1].set_title('Velocity', loc='left', pad=-17, y=1, x=0.005)
    axs[2].set(ylabel='m/s2')
    axs[2].set_title('Acceleration', loc='left', pad=-17, y=1, x=0.005)
    axs[3].set(ylabel='mm')
    axs[3].set_title('Positioning error', loc='left', pad=-17, y=1, x=0.005)

    for ax in axs:
        ax.grid(True)

    plt.subplots_adjust(top=0.979,
                        bottom=0.039,
                        left=0.041,
                        right=0.992,
                        hspace=0.05,
                        wspace=0.2)

    figManager = plt.get_current_fig_manager()
    figManager.full_screen_toggle()

    plt.show()


if __name__ == '__main__':
    with open('tests/datatest.log', 'r') as file:
        plotdata3(file)
