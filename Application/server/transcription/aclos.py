import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
import pyaudio
import math
from utils.general import loadNormalizedSoundFIle, create_sine, fft_to_hz
from utils.plots import plot_spectrum_line_component, plot_spectrogram, plot_correlation, plot_pitches, plot_correlogram, plot_interpolated_correlation
from utils.profile import profile, print_prof_data
from utils.cepstrumUtils import lifterOnPowerSpec, LifterType
from scipy.interpolate import interp1d

# Autocorrelation of Log Spectrum
# Paper: https://www.researchgate.net/publication/232643468_Robust_method_of_measurement_of_fundamental_frequency_by_ACLOS_autocorrelation_of_log_spectrum
# wartości domyślne są zeby było tak samo jak w pracy naukowej
# https://dsp.stackexchange.com/questions/736/how-do-i-implement-cross-correlation-to-prove-two-audio-files-are-similar
# https://books.google.pl/books?id=zfVeDwAAQBAJ&pg=PA240&lpg=PA240&dq=fft+log+abs&source=bl&ots=WeVYfedbB6&sig=ACfU3U0WD7QNHPVm08eaFC-0B8vr8mHKVA&hl=pl&sa=X&ved=2ahUKEwjWi_3m7NTmAhUQuaQKHcTCAM0Q6AEwA3oECAcQAQ#v=onepage&q=fft%20log%20abs&f=false
def aclos(data, sampleRate = 1024, frameWidth = 512, spacing = 512):
    correlogram = []
    interpolatedAutocorrelogram = []
    spectra = []
    bestLag = []
    bestFq = []
    lifteredSpectra = []
    hann = np.hanning(frameWidth)
    zeroPadding = np.zeros(frameWidth)
    fftToFq = fft_to_hz(sampleRate, frameWidth)
    fqMaxError = sampleRate // frameWidth


    def ac(data, minLag, maxLag):
        # w teiri dwie pętle, ale *= leci po wszystkich elementach
        n = len(data)
        result = list(np.zeros(minLag))
        for lag in range(minLag, maxLag):
            sumArray = np.zeros(n + lag)
            sumArray[:n] = data
            sumArray[:n-lag] *= data[lag:]
            sum = np.sum(sumArray[:n-lag])
            result.append(float(sum/(n-lag)))

        interpolated = interp1d(np.arange(0, len(result)), result, kind='cubic')
        return result, interpolated

    def countBestFq(interpolatedAutocorrelation, dataLen, interpolMultipler = 10):
        interp_x = np.linspace(0, dataLen-1, num=dataLen*interpolMultipler)
        argmax = np.argmax(interpolatedAutocorrelation(interp_x))
        correlationArgMax = int(np.round(argmax / interpolMultipler))
        delta = argmax - (correlationArgMax * interpolMultipler)
        bestFq = fftToFq[correlationArgMax] + (fqMaxError * delta / interpolMultipler)
        return bestFq        

    for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing)))):
        frame = data[i*spacing:i*spacing+frameWidth] * hann
        frame = np.concatenate((frame, zeroPadding))
        frameComplex = fft(frame)
        fftLen = int(np.floor(len(frameComplex)/2))
        powerSpec = abs(frameComplex)
        lifteredPowerSpec = lifterOnPowerSpec(powerSpec, LifterType.sine, 8)

        powerSpec = powerSpec[:fftLen]
        lifteredPowerSpec = lifteredPowerSpec[:fftLen]

        autocorrelation, interpolatedAutocorrelation = ac(lifteredPowerSpec, 5, frameWidth // 2 + 1)

        correlogram.append(autocorrelation,)
        interpolatedAutocorrelogram.append(interpolatedAutocorrelation)
        spectra.append(powerSpec)
        lifteredSpectra.append(lifteredPowerSpec)
        bestLag.append(np.argmax(autocorrelation))
        bestFq.append(countBestFq(interpolatedAutocorrelation, len(autocorrelation)))


    return correlogram, interpolatedAutocorrelogram, bestLag, bestFq, spectra

if __name__ == "__main__":
    frameWidth = 2048
    spacing = 512
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')
    #filePath = path.join(filePath, '../test_sounds/Chopin_prelude28no.4inEm/chopin_prelude_28_4.wav')
    #filePath = path.join(filePath, '../test_sounds/EmPiano/Em.wav')
    #file_path = '../test_sounds/Sine_sequence.wav'
    #filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)
    sine_data = create_sine(440, sampleRate, 5)
    sine_data += (create_sine(880, sampleRate, 5) * 0.4)
    sine_data += (create_sine(1320, sampleRate, 5) * 0.2)


    correlogram, interpolatedAutocorrelogram, bestLag, bestFq, spectra = aclos(data, sampleRate, frameWidth, spacing)
    plot_spectrogram(spectra, spacing, sampleRate, showColorbar=False, language="pl")
    
    # plot_correlogram(correlogram, spacing, sampleRate, language='pl', showColorbar=False)
    # plot_pitches(bestFq, spacing, sampleRate, language='pl')
    # fig = plot_spectrum_line_component(spectra[5], sampleRate, data[:frameWidth])
    # plt.show()
    # plot_interpolated_correlation(interpolatedAutocorrelogram[10], correlogram[10], language='pl')


    print("ok")