## W tym pliku znajduje się implementacja algorytmu ACLOS

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
import math
from utils.general import loadNormalizedSoundFile, create_sine, fft_to_hz
from utils.plots import plot_spectrum_line_component, plot_spectrogram, plot_correlation, plot_pitches, plot_correlogram, plot_interpolated_correlation
from utils.custom_profile import profile, print_prof_data
from utils.cepstrumUtils import lifterOnPowerSpec, LifterType
from scipy.interpolate import interp1d
from io import BytesIO

def aclos(data, sampleRate = 1024, frameWidth = 512, spacing = 512, sizeOfZeroPadding = 512, disableTqdm = True):
    correlogram = []
    interpolatedAutocorrelogram = []
    spectra = []
    bestLag = []
    bestFq = []
    lifteredSpectra = []
    hann = np.hanning(frameWidth)
    zeroPadding = np.zeros(sizeOfZeroPadding)
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

    def countBestFq(interpolatedAutocorrelation, dataLen, interpolMultiplier = 10):
        interp_x = np.linspace(0, dataLen-1, num=dataLen*interpolMultiplier)
        argmax = np.argmax(interpolatedAutocorrelation(interp_x))
        correlationArgMax = int(np.round(argmax / interpolMultiplier))
        delta = argmax - (correlationArgMax * interpolMultiplier)
        bestFq = fftToFq[correlationArgMax] + (fqMaxError * delta / interpolMultiplier)
        return bestFq

    for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing))), disable=disableTqdm):
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


    return bestFq, correlogram, interpolatedAutocorrelogram, bestLag, spectra

## Funkcja do użytku przez serwer
def transcribe_by_aclos_wrapped(filePath):
    frameWidth = 2048
    spacing = 512
    sampleRate, data = loadNormalizedSoundFile(filePath)
    bestFq, correlogram, _, _, spectra = aclos(data, sampleRate, frameWidth, spacing, frameWidth)


    fig, _ = plot_pitches(bestFq, spacing, sampleRate, show=False, language="pl")
    fig2, _ = plot_spectrogram(spectra, spacing, sampleRate, show=False, language="pl")
    fig3, _ = plot_correlogram(correlogram, spacing, sampleRate, show=False, language="pl")


    pitchesFig, correlogramFig, spectrogramFig = BytesIO(), BytesIO(), BytesIO()
    fig.savefig(pitchesFig, format="png")
    fig2.savefig(spectrogramFig, format="png")
    fig3.savefig(correlogramFig, format="png")

    return pitchesFig, correlogramFig, spectrogramFig

if __name__ == "__main__":
    frameWidth = 2048
    spacing = 512
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    sampleRate, data = loadNormalizedSoundFile(filePath)


    bestFq, correlogram, interpolatedAutocorrelogram, bestLag, spectra = aclos(data, sampleRate, frameWidth, spacing, frameWidth)
    plot_interpolated_correlation(interpolatedAutocorrelogram[10], correlogram[10], language='pl')


    print("ok")