# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plot
from numpy.fft import fft, fftshift

def hannWindow(path):
    hannWindow = np.hanning(2048)
    plot.plot(hannWindow)
    plot.title("Okno Hanna")
    plot.ylabel("Amplituda")
    plot.xlabel("Czas (w samplach)")
    plot.savefig(path)
    plot.close()
    
def hammingWindow(path):
    hamming = np.hamming(2048)
    plot.plot(hamming)
    plot.title("Okno Hamminga")
    plot.ylabel("Amplituda")
    plot.xlabel("Czas (w samplach)")
    plot.savefig(path)
    plot.close()

def rectangleWindow(path):
    rectangle = np.zeros(2048)
    rectangle.fill(1)
    rectangle[0] = 0
    rectangle[-1] = 0
    plot.plot(rectangle)
    plot.title("Okno prostokątne")
    plot.ylabel("Amplituda")
    plot.xlabel("Czas (w samplach)")
    plot.savefig(path)
    plot.close()