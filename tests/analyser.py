import matplotlib.pyplot as plt
from io import TextIOWrapper
from traceback import format_exc
from typing import Tuple
from scipy.signal import cspline1d, cspline1d_eval
import numpy as np
from scipy.interpolate import CubicSpline, splrep, BSpline


def calcder(t: list[float], x: list[float], mult: float = 1) -> Tuple[list[float], list[float]]:
    res = []
    if len(t) == len(x):
        for i in range(1, len(t)):
            dx = x[i]-x[i-1]
            dt = t[i]-t[i-1]
            d = dx/dt*mult
            res.append(d)
        return t[1:], res
    else:
        raise Exception('List length mast be equal')


def sumaver(inp: list[float], aver: int) -> list[float]:
    res = []
    for i in range(len(inp)):
        if i < aver:
            res.append(inp[i])
        else:
            a = inp[i]
            for ii in range(1, aver):
                a += inp[i-ii]
            a = a/aver
            res.append(a)
    return res


def plotdata(file: TextIOWrapper):
    dt = 4.1  # y latency ms
    x = []
    y = []
    dxy = []
    tx = []
    ty = []
    i = 0
    file.seek(0)
    for line in file.readlines():
        data = line.strip().split('\t')
        try:
            if not i:
                x0 = float(data[0])
                y0 = float(data[1])
                py = y0
            cx = ((float(data[0])-x0)/100)  # current step position
            x.append(cx)
            cy = -(float(data[1])-y0)/1000000  # current reader position
            y.append(cy)
            dxy.append(cx-cy)
            tx.append(i/1000)
            ty.append((i-dt)/1000)
            i += 1
        except:
            print(f'Failed to read data from line {i}: {data}\n{format_exc()}')

    fig, axs = plt.subplots(4, sharex=True)
    print(f'Got data with {len(y)} points')
    axs[0].plot(ty, y)
    axs[0].plot(tx, x)
    axs[3].plot(tx, dxy)
    tv, vy = calcder(ty, y, 1/1000)
    averam = 5
    vy = sumaver(vy, averam)
    ta, ay = calcder(tv, vy)
    ay = sumaver(ay, averam)
    vx = calcder(tx, x, 1/1000)[1]
    vx = sumaver(vx, averam)
    ax = calcder(tv, vx)[1]
    ax = sumaver(ax, averam)
    axs[1].plot(tv, vx)
    axs[1].plot(tv, vy)
    axs[2].plot(ta, ax)
    axs[2].plot(ta, ay)
    axs[0].set(ylim=(-10, 30), ylabel='mm')
    axs[1].set(ylim=(-1, 1), ylabel='m/s')
    axs[2].set(ylim=(-10, 10), ylabel='m/s2')
    axs[3].set(ylim=(-2, 2), ylabel='mm')
    for ax in axs:
        ax.label_outer()
        ax.grid(True)
    fig.subplots_adjust(hspace=0.05)
    plt.show()


def readdata(file: TextIOWrapper) -> Tuple[list[float], list[float]]:
    lines = file.readlines()
    x = np.empty(len(lines), float)
    y = np.empty(len(lines), float)
    i = 0
    for line in lines:
        data = line.strip().split('\t')
        try:
            if not i:
                x0 = float(data[0])
                y0 = float(data[1])
            x[i] = ((float(data[0])-x0)/100)  # current step position
            # x[i]=cx
            y[i] = -(float(data[1])-y0)/1000000  # current reader position
            # y.append(cy)
            i += 1
        except:
            print(f'Failed to read data from line {i}: {data}\n{format_exc()}')
    return x, y


def getdelay(x: np.ndarray, y: np.ndarray, maxdel: float = 20, steps: int = 100, maxdelta: float = 10) -> float:
    spl = CubicSpline(range(len(y)), y)
    deltas = []
    delays = np.linspace(0, maxdel, steps)
    for delay in delays:
        times = np.linspace(delay, len(y)+delay, len(y))
        new_ys = spl(times)
        delta = 0
        for ii in range(len(y)):
            cdelta = abs(x[ii]-new_ys[ii])
            if cdelta < maxdelta:
                delta += cdelta
        deltas.append(delta)
    sdels = splrep(delays, deltas, w=np.full(100, 1/10))
    ll = BSpline(*sdels)(delays)
    return delays[np.argmin(ll)]


if __name__ == '__main__':
    with open('tests/datatest.log', 'r') as file:
        # plotdata(file)
        x, y = readdata(file)
        spl = cspline1d(y)
        ty = np.arange(4.6, len(x)+4.6, 1)
        sy = cspline1d_eval(spl, ty)
        # graph = plt.plot(y)[0]
        # plt.plot(x)
        # plt.show()
        spl2 = CubicSpline(range(len(y)), y)
        deltas = []
        delays = np.linspace(0, 20, 100)
        for delay in delays:
            # print(delay)
            times = np.linspace(delay, len(y)+delay, len(y))
            new_ys = spl2(times)
            delta = 0
            for ii in range(len(y)):
                cdelta = abs(x[ii]-new_ys[ii])
                if cdelta < 10:
                    delta += cdelta
            deltas.append(delta)
            # graph.set_ydata(new_ys)
            # plt.draw()
            # plt.pause(0.2)
        sdels = splrep(delays, deltas, w=np.full(100, 1/10))
        ll = BSpline(*sdels)(delays)
        print(delays[np.argmin(ll)])
        plt.plot(delays, ll)
        plt.grid()
        plt.show()
