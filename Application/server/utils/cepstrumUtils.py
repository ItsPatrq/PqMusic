import numpy as np
from scipy.fftpack import fft, ifft
import enum

class LifterType(enum.Enum):
    sine = 1
    triangle = 2
    rectangle = 3

def lifterOnLogSpec(spec, lifterType=LifterType.sine, coefficient=18):
    cepst = ifft(spec)
    lifteredCeps = lifterOnCeps(cepst, lifterType, coefficient)
    return ceps_to_log_spec(lifteredCeps)

def lifterOnPowerSpec(spec, lifterType=LifterType.sine, coefficient=2):
    cepst = ifft(np.log(spec)).real
    lifteredCeps = lifterOnCeps(cepst, lifterType, coefficient)
    return ceps_to_pow_spec(lifteredCeps)


def lifterOnCeps(ceps, lifterType=LifterType.triangle, coefficient=2):
    if coefficient <= 0: raise Exception("Liftering coefficient has to be greater then 0")
    if coefficient <= 1 and lifterType == LifterType.triangle: raise Exception("Liftering coefficient has to be greater then 1 with triangular liftering")

    k = np.arange(len(ceps))
    h = (coefficient/2.)
    def f(lifterType):
        lift = {
            LifterType.sine: 1 + h * np.sin(np.pi*k/coefficient),
            LifterType.triangle: 1 + h * (k - 1) / (coefficient - 1),
            LifterType.rectangle: np.ones(len(ceps))
        }[lifterType]
        #lift[coefficient:] *=0
        return lift

    lift = f(lifterType)

    return ceps * lift

def real_cepst_from_signal(data):
    spectrum = fft(data)
    logSp = np.log(np.abs(spectrum))
    ceps = np.abs(ifft(logSp)) ** 2
    return ceps, logSp, spectrum

def ceps_to_log_spec(ceps):
    return fft(ceps)

def ceps_to_pow_spec(ceps):
    return np.exp(fft(ceps).real)

def complex_cepst_from_signal(data):
    def unwrap(phase):
        n = np.size(phase)
        unwrapped = np.unwrap(phase)
        center = (n + 1) // 2
        ndelay = np.array(np.round(unwrapped[center] / np.pi))
        unwrapped -= np.pi * ndelay[..., None] * np.arange(n) / center
        return unwrapped, ndelay

    spectrum = fft(data)
    logSpec = np.log(np.abs(spectrum)) 
    unwrapped_phase, ndelay = unwrap(np.angle(spectrum))
    logSpWithIm = logSpec + 1j * unwrapped_phase
    ceps = ifft(logSpWithIm).real

    return ceps, ndelay, spectrum, logSpec

def inverse_complex_cepstrum(ceps, ndelay):
    def wrap(phase, ndelay):
        ndelay = np.array(ndelay)
        samples = phase.shape[-1]
        center = (samples + 1) // 2
        wrapped = phase + np.pi * ndelay[..., None] * np.arange(samples) / center
        return wrapped
    log_spectrum = np.fft.fft(ceps)
    spectrum = np.exp(log_spectrum.real + 1j * wrap(log_spectrum.imag, ndelay))
    x = np.fft.ifft(spectrum).real
    return x


def complex_cepst_from_signal_gpu(data):
    def unwrap(phase):
        n = np.size(phase)
        unwrapped = np.unwrap(phase)
        center = (n + 1) // 2
        ndelay = np.array(np.round(unwrapped[center] / np.pi))
        unwrapped -= np.pi * ndelay[..., None] * np.arange(n) / center
        return unwrapped, ndelay

    spectrum = fft(data)
    logSpec = np.log(np.abs(spectrum)) 
    unwrapped_phase, ndelay = unwrap(np.angle(spectrum))
    logSpWithIm = logSpec + 1j * unwrapped_phase
    ceps = ifft(logSpWithIm).real

    return ceps, ndelay, spectrum, logSpec

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from utils.general import loadNormalizedSoundFIle
    
    def test1():
        filePath = path.dirname(path.abspath(__file__))
        filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')
        fs, signal = loadNormalizedSoundFIle(filePath)
        samples = len(signal)
        t = np.arange(samples) / fs
        ceps, ndelay, spectrum, logSp = complex_cepst_from_signal(signal)
        fig = plt.figure()
        ax1 = fig.add_subplot(512)
        ax1.plot(t, ceps)
        ax1.set_xlabel('quefrency in seconds')
        ax1.set_xlim(0.005, 0.015)
        ax1.set_ylim(-5., +10.)
        ceps[(abs(ceps) < 0.01)] = 0
        print(ceps[1])
        y = inverse_complex_cepstrum(ceps, ndelay)
        ax0 = fig.add_subplot(511)
        ax0.plot(t, signal,'-')
        ax0.plot(t, y ,'--')
        ax0.legend(['data', 'lifter'], loc='best')
        ax0.set_xlabel('time in seconds')
        ax0.set_xlim(0.0, 0.05)

        fftFromSignal = fft(signal)
        fftFromLifteredSignal = fft(y)
        ax4 = fig.add_subplot(514)
        ax4.plot(t[:(len(t)//2)], fftFromSignal.real[:(len(t)//2)], '-')
        ax4.plot(t[:(len(t)//2)], fftFromLifteredSignal.real[:(len(t)//2)], '--')
        ax4.legend(['data', 'lifter'], loc='best')

        ax4.set_xlabel('fq in seconds')

        ifftFromFft = ifft(fftFromSignal)
        ax5 = fig.add_subplot(515)
        ax5.plot(t, ifftFromFft)
        ax5.set_xlabel('time in seconds')
        ax5.set_xlim(0.0, 0.05)
        plt.show()

    def test2():
        filePath = path.dirname(path.abspath(__file__))
        filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')
        fs, signal = loadNormalizedSoundFIle(filePath)
        signal = signal * 40
        samples = len(signal)
        t = np.arange(samples) / fs

        ceps, ndelay, spectrum, logSp = complex_cepst_from_signal(signal)
        fig = plt.figure()
        ax0 = fig.add_subplot(511)
        ax0.plot(t, signal)
        ax0.set_xlabel('time in seconds')
        ax0.set_xlim(0.0, 0.05)
        ax1 = fig.add_subplot(512)
        ax1.plot(t, ceps)
        ax1.set_xlabel('quefrency in seconds')
        ax1.set_xlim(0.005, 0.015)
        ax1.set_ylim(-5., +10.)
        ax2 = fig.add_subplot(513)
        ax2.plot(t[:(len(t)//2)], spectrum.real[:(len(t)//2)])
        ax2.set_xlabel('fq in seconds')
        plt.show()

    def test3():
        filePath = path.dirname(path.abspath(__file__))
        filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')
        fs, signal = loadNormalizedSoundFIle(filePath)
        samples = 2048 * 2
        t = np.arange(samples) / fs
        spec =  np.abs(fft(signal[(samples * 2):(samples*3)]))
        #ceps, ndelay, spectrum, logSp = complex_cepst_from_signal(signal[:2048])
        #liftering
        print(spec)
        liftered = lifterOnPowerSpec(spec, LifterType.sine, 10)
        #triangular = lifterOnPowerSpec(spec, LifterType.triangle, 1)
        print(spec, liftered)
        #end of liftering

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(t[:(len(t)//2)], spec[:(len(t)//2)], '--')
        ax1.plot(t[:(len(t)//2)], liftered[:(len(t)//2)], '-')
        #ax1.plot(t[:(len(t)//2)], triangular[:(len(t)//2)], '-')
        ax1.legend(['spektrum mocy', 'przefiltrowane spektrum mocy'], loc='best')

        plt.show()

    test3()
