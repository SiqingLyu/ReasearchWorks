from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np


def plot_SD(x,y):

    plt.hist2d(x, y, bins=40, norm=LogNorm())
    plt.colorbar()
    plt.show()
