import time
import random
import numpy as np
import matplotlib.pylab as plt

RESL = 20
TIME = 0.05
AMPL = 32000

x = np.linspace(-np.pi, np.pi, RESL)

def generate_data(i):
    return [[np.sin(x[i])*AMPL]*3]*3

if __name__ == '__main__':
    idx = 0
    tmp = 0
    xdata = []
    ydata = []
    axes = plt.gca()
    axes.set_xlim(0, 1000)
    axes.set_ylim(-AMPL, AMPL)
    line, = axes.plot(xdata, ydata, 'r-')

    while True:
        v = generate_data(idx)
        idx = (idx + 1) % RESL
        print(v)
        time.sleep(TIME)
        
        tmp += 1
        xdata.append(tmp)
        ydata.append(v[0][0])
        line.set_xdata(xdata)
        line.set_ydata(ydata)
        plt.draw()
        plt.pause(1e-17)

    plt.show()
