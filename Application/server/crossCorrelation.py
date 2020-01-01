from scipy import signal
import numpy as np
from obspy.core import read
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft, fftshift
t1 = np.linspace(-1, 1, 2 * 100, endpoint=False)
sig1 = signal.gausspulse(t1, fc=5)
plt.figure(figsize=(10, 8))
plt.plot(t1, sig1, 'r')
plt.show()


def nextpow2(i):
    '''
    Find the next power 2 number for FFT
    '''

    n = 1
    while n < i:
        n *= 2
    return n


def shift_signal_in_frequency_domain(datin, shift):
    '''
    This is function to shift a signal in frequency domain. 
    The idea is in the frequency domain, 
    we just multiply the signal with the phase shift. 
    '''
    Nin = len(datin)

    # get the next power 2 number for fft
    N = nextpow2(Nin + np.max(np.abs(shift)))

    # do the fft
    fdatin = np.fft.fft(datin, N)

    # get the phase shift, shift here is D in the above explanation
    ik = np.array([2j*np.pi*k for k in range(0, N)]) / N
    fshift = np.exp(-ik*shift)

    # multiple the signal with shift and transform it back to time domain
    datout = np.real(np.fft.ifft(fshift * fdatin))

    # only get the data have the same length as the input signal
    datout = datout[0:Nin]

    return datout


# This is the amount we will move
nShift = 50

# generate the 2nd signal
sig2 = shift_signal_in_frequency_domain(sig1, nShift)

# plot two signals together
plt.figure(figsize=(10, 8))
plt.plot(sig1, 'r', label='signal 1')
plt.plot(sig2, 'b', label='signal 2')
plt.legend()
plt.show()

#Frequency domain cross correlation


def cross_correlation_using_fft(x, y):
    f1 = fft(x)

    # flip the signal of y
    f2 = fft(np.flipud(y))
    cc = np.real(ifft(f1 * f2))

    return fftshift(cc)

# shift &lt; 0 means that y starts 'shift' time steps before x
# shift &gt; 0 means that y starts 'shift' time steps after x


def compute_shift(x, y):
    # we make sure the length of the two signals are the same
    assert len(x) == len(y)
    c = cross_correlation_using_fft(x, y)
    assert len(c) == len(x)
    zero_index = int(len(x) / 2) - 1
    shift = zero_index - np.argmax(c)
    return shift

calculate_shift = compute_shift(sig1, sig2)


print('The shift we get from cross correlation is %d, the true shift should be 50' %calculate_shift)
