import matplotlib.pyplot as plt
from io import TextIOWrapper

def plotdata(file:TextIOWrapper):
    # file = open('tests/recieve.log', 'r')
    x = []
    y = []
    t = []
    i = 0
    for line in file.readlines():
        data = line.strip().split('\t')
        try:
            if not i:
                x0=float(data[0])
                y0 = float(data[1])
            x.append((float(data[0])-x0)/100)
            y.append((float(data[1])-y0)/10000/256)
            t.append(i/1000)
            i+=1
        except:
            print(f'Failed to read data from line {i}: {data}')

    fig, ax = plt.subplots()

    ax.plot(t,y)
    # ax.plot(t,x)
    ax.set(xlim=(t[0], t[-1]))
    plt.show()
