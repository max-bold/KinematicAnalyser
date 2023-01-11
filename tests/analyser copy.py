import matplotlib.pyplot as plt
from io import TextIOWrapper
from traceback import format_exc
from typing import Tuple
import numpy as np
from scipy.interpolate import CubicSpline, splrep, BSpline, splev, splder
from time import sleep


# def calcder(t: list[float], x: list[float], mult: float = 1) -> Tuple[list[float], list[float]]:
#     res = []
#     if len(t) == len(x):
#         for i in range(1, len(t)):
#             dx = x[i]-x[i-1]
#             dt = t[i]-t[i-1]
#             d = dx/dt*mult
#             res.append(d)
#         return t[1:], res
#     else:
#         raise Exception('List length mast be equal')


# def sumaver(inp: list[float], aver: int) -> list[float]:
#     res = []
#     for i in range(len(inp)):
#         if i < aver:
#             res.append(inp[i])
#         else:
#             a = inp[i]
#             for ii in range(1, aver):
#                 a += inp[i-ii]
#             a = a/aver
#             res.append(a)
#     return res


# def plotdata(file: TextIOWrapper):
#     dt = 4.1  # y latency ms
#     x = []
#     y = []
#     dxy = []
#     tx = []
#     ty = []
#     i = 0
#     file.seek(0)
#     for line in file.readlines():
#         data = line.strip().split('\t')
#         try:
#             if not i:
#                 x0 = float(data[0])
#                 y0 = float(data[1])
#                 py = y0
#             cx = ((float(data[0])-x0)/100)  # current step position
#             x.append(cx)
#             cy = -(float(data[1])-y0)/1000000  # current reader position
#             y.append(cy)
#             dxy.append(cx-cy)
#             tx.append(i/1000)
#             ty.append((i-dt)/1000)
#             i += 1
#         except:
#             print(f'Failed to read data from line {i}: {data}\n{format_exc()}')

#     fig, axs = plt.subplots(4, sharex=True)
#     print(f'Got data with {len(y)} points')
#     axs[0].plot(ty, y)
#     axs[0].plot(tx, x)
#     axs[3].plot(tx, dxy)
#     tv, vy = calcder(ty, y, 1/1000)
#     averam = 5
#     vy = sumaver(vy, averam)
#     ta, ay = calcder(tv, vy)
#     ay = sumaver(ay, averam)
#     vx = calcder(tx, x, 1/1000)[1]
#     vx = sumaver(vx, averam)
#     ax = calcder(tv, vx)[1]
#     ax = sumaver(ax, averam)
#     axs[1].plot(tv, vx)
#     axs[1].plot(tv, vy)
#     axs[2].plot(ta, ax)
#     axs[2].plot(ta, ay)
#     axs[0].set(ylim=(-10, 30), ylabel='mm')
#     axs[1].set(ylim=(-1, 1), ylabel='m/s')
#     axs[2].set(ylim=(-10, 10), ylabel='m/s2')
#     axs[3].set(ylim=(-2, 2), ylabel='mm')
#     for ax in axs:
#         ax.label_outer()
#         ax.grid(True)
#     fig.subplots_adjust(hspace=0.05)
#     plt.show()


# def plotdata2(file: TextIOWrapper):
#     data = readdata(file, delay=4, timestep=1/1000)
#     filtered = filtedif(data, maxdif=2)
#     smoothed = smoothdata(filtered, window=10)
#     splcom = CubicSpline(*filternan(smoothed[:, 0], smoothed[:, 1]))
#     splmeas = CubicSpline(*filternan(smoothed[:, 0], smoothed[:, 2]))

#     fig, axs = plt.subplots(4, sharex=True)
#     axs[0].plot(smoothed[:, 0], splcom(smoothed[:, 0]), label='command')
#     axs[0].plot(smoothed[:, 0], splmeas(smoothed[:, 0]), label='measurement')
#     axs[3].plot(smoothed[:, 0], smoothed[:, 3])
#     axs[1].plot(smoothed[:, 0],
#                 np.multiply(splcom(smoothed[:, 0], nu=1), 1/1000),
#                 label='command')
#     axs[1].plot(smoothed[:, 0],
#                 np.multiply(splmeas(smoothed[:, 0], nu=1), 1/1000),
#                 label='measurement')
#     axs[2].plot(smoothed[:, 0],
#                 np.multiply(splcom(smoothed[:, 0], nu=2), 1/1000),
#                 label='command')
#     axs[2].plot(smoothed[:, 0],
#                 np.multiply(splmeas(smoothed[:, 0], nu=2), 1/1000),
#                 label='measurement')
#     axs[0].set(ylim=(-10, 30), ylabel='mm')
#     axs[0].set_title('Position', loc='left', pad=-17, y=1, x=0.005)
#     axs[1].set(ylim=(-1, 1), ylabel='m/s')
#     axs[1].set_title('Velocity', loc='left', pad=-17, y=1, x=0.005)
#     axs[2].set(ylim=(-10, 10), ylabel='m/s2')
#     axs[2].set_title('Acceleration', loc='left', pad=-17, y=1, x=0.005)
#     axs[3].set(ylim=(-2, 2), ylabel='mm')
#     axs[3].set_title('Positioning error', loc='left', pad=-17, y=1, x=0.005)
#     for ax in axs:
#         ax.label_outer()
#         ax.grid(True)
#     fig.subplots_adjust(hspace=0.05)
#     plt.subplots_adjust(top=0.979,
#                         bottom=0.039,
#                         left=0.041,
#                         right=0.992,
#                         hspace=0.05,
#                         wspace=0.2)
#     figManager = plt.get_current_fig_manager()
#     figManager.full_screen_toggle()
#     plt.show()


def plotdata3(file: TextIOWrapper):
    data = readdata(file, delay=4, timestep=1/1000)
    filtered = filtedif(data, maxdif=2)
    smoothed = splinesmooth(filtered, 0.01)
    vel = splinesmooth(filtered, 0.01, 1, 1/1000)
    acc = splinesmooth(vel, 0.01, 1)

    fig, axs = plt.subplots(4, sharex=True)

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
    axs[2].set( ylabel='m/s2')
    axs[2].set_title('Acceleration', loc='left', pad=-17, y=1, x=0.005)
    axs[3].set(ylabel='mm')
    axs[3].set_title('Positioning error', loc='left', pad=-17, y=1, x=0.005)

    for ax in axs:
        # ax.label_outer()
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


# def getdelay(x: np.ndarray, y: np.ndarray, maxdel: float = 20, steps: int = 100, maxdelta: float = 10) -> float:
#     spl = CubicSpline(range(len(y)), y)
#     deltas = []
#     delays = np.linspace(0, maxdel, steps)
#     for delay in delays:
#         times = np.linspace(delay, len(y)+delay, len(y))
#         new_ys = spl(times)
#         delta = 0
#         for ii in range(len(y)):
#             cdelta = abs(x[ii]-new_ys[ii])
#             if cdelta < maxdelta:
#                 delta += cdelta
#         deltas.append(delta)
#     sdels = splrep(delays, deltas, w=np.full(100, 1/10))
#     ll = BSpline(*sdels)(delays)
#     return delays[np.argmin(ll)]


def filtedif(data: np.ndarray, maxdif: float = 10, both=False) -> np.ndarray:
    res = np.copy(data)
    for row in res:
        if row[3] > maxdif:
            if both:
                row[1] = np.nan
            row[2] = np.nan
            row[3] = np.nan
    return res


# def wsmooth(data: np.ndarray, window: int = 3, exp: float = 1) -> np.ndarray:
#     res = np.full(data.size, np.nan)
#     w2 = int((window-1)/2)
#     for i in range(data.size):
#         sum = 0
#         n = 0
#         for ii in range(-w2, w2+1):
#             if ii+i > 0 and ii+i < data.size-1 and not np.isnan(data[i+ii]):
#                 w = 1/(exp**abs(ii))
#                 sum += data[ii+i]*w
#                 n += w
#         if n:
#             res[i] = sum/n
#     return res


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


# def smoothdata(data: np.ndarray, window: int = 9, exp: float = 1):
#     res = np.empty(data.shape)
#     res[:, 0] = data[:, 0]
#     res[:, 1] = wsmooth(data[:, 1], window, exp)
#     res[:, 2] = wsmooth(data[:, 2], window, exp)
#     res[:, 3] = np.abs(np.subtract(res[:, 1], res[:, 2]))
#     return res


def splinesmooth(data: np.ndarray, smootness: float, der: int = 0, mult: float = 1) -> np.ndarray:
    res = np.empty_like(data)
    res[:, 0] = data[:, 0]
    for i in range(1, 3):
        spl = splrep(*filternan(data[:, 0], data[:, i]), s=smootness)
        res[:, i] = np.multiply(splev(data[:, 0], spl, der=der), mult)
    res[:, 3] = np.abs(np.subtract(res[:, 1], res[:, 2]))
    return res


# def datader(data: np.ndarray, der: int = 1, mult: float = 1) -> np.ndarray:
#     res = np.full_like(data, np.nan)
#     res[:, 0] = data[:, 0]
#     for i in range(1, data.shape[0]):
#         for c in range(1, 3):
#             if (not np.isnan(data[i-1, c])) and (not np.isnan(data[i, c])):
#                 res[i, c] = (data[i, c]-data[i-1, c]) / \
#                     (data[i, 0]-data[i-1, 0])*mult
#     res[:, 3] = np.abs(np.subtract(res[:, 1], res[:, 2]))
#     if der > 1:
#         return datader(res, der-1)
#     else:
#         return res


if __name__ == '__main__':
    with open('tests/datatest.log', 'r') as file:
        plotdata3(file)
