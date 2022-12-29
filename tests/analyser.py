import matplotlib.pyplot as plt
from io import TextIOWrapper
from traceback import format_exc
from typing import Tuple


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
    averam=5
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


if __name__ == '__main__':
    with open('tests/datatest.log', 'r') as file:
        plotdata(file)