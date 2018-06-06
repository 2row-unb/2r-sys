import time
import random
import numpy as np
import matplotlib.pylab as plt

RESL = 200
TIME = 0.0000
AMPL = 500
X_LEN = 250
ERROR = AMPL * 0.2

x = np.linspace(-np.pi, np.pi, RESL+1)[:-1]


def data_generator(func=None):
    idx = 0
    while True:
        v = generate_data(idx)
        idx = (idx + 1) % RESL
        yield func(v) if func else v


def generate_data(i):
    noise = (random.random() * ERROR) - ERROR / 2.0
    return [np.sin(x[i])*AMPL + noise]*18


def run():
    idx = 0
    tmp = 0
    xdata = []
    ydata = []
    axes = plt.gca()
    axes.set_xlim(0, X_LEN)
    axes.set_ylim(-AMPL, AMPL)
    line, = axes.plot(xdata, ydata, 'r-')

    while True:
        v = generate_data(idx)
        idx = (idx + 1) % RESL

        print(v)
        time.sleep(TIME)

        tmp += 1
        xdata.append(tmp)
        ydata.append(v[0])

        if tmp > X_LEN:
            ydata = ydata[1:]
            xdata.pop()

        line.set_xdata(xdata)
        line.set_ydata(ydata)
        plt.draw()
        plt.pause(1e-17)

    plt.show()


if __name__ == '__main__':
    run()
