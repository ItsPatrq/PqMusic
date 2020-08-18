## W tym pliku znajduje się implementacja algorytmu wykrywającego F0 przy pomocy metod cepstrum na GPU

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
import math
from utils.general import loadNormalizedSoundFile, create_sine
from utils.plots import plot_spectrum_line_component_only, plot_spectrum_line_components, plot_spectrogram, plot_cepstrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal
from utils.cepsUtilsGpu import CepsUtilsGpu
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
from reikna.fft import FFT as gpu_fft
from reikna.cluda import dtypes, cuda_api
from io import BytesIO

## Analiza F0 przy pomocy cepstrum na GPU
def cepstrumF0AnalysisGpu (api, thr, compiledCepstrum, data, sampleRate = 1024, frameWidth = 512, spacing = 512, sizeOfZeroPadding = 512):
    if compiledCepstrum is None:
        params = dict(Fs=sampleRate, NFFT=frameWidth, noverlap=frameWidth-spacing, pad_to=frameWidth+sizeOfZeroPadding)
        compiledCepstrum = CepsUtilsGpu(
            data, NFFT=params['NFFT'], noverlap=params['noverlap'], pad_to=params['pad_to']).compile(thr)

    data_dev = thr.to_device(data)
    ceps_dev = thr.empty_like(compiledCepstrum.parameter.output)
    compiledCepstrum(ceps_dev, data_dev)
    cepstra = ceps_dev.get()
    bestFq = []
    for cepst in cepstra.T:
        maxperiod = np.argmax(cepst)
        if maxperiod == 0:
            bestFq.append(0)
        else:
            bestFq.append(sampleRate/maxperiod)
    return cepstra, bestFq, compiledCepstrum


if __name__ == "__main__":
    frameWidth = 2048
    spacing = 512
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    sampleRate, data = loadNormalizedSoundFile(filePath)

    pycuda.driver.init() # pylint: disable=no-member
    dev = pycuda.driver.Device(0) # pylint: disable=no-member
    ctx = dev.make_context()
    api = cuda_api()
    thr = api.Thread.create()
    
    compiledCepstrum = None
    for i in range(0, 1000):
        cepstra, bestFq, compiledCepstrum = cepstrumF0AnalysisGpu(api, thr, compiledCepstrum, np.array(data), sampleRate, 4096, 1024, 8192)

    plot_cepstrogram(cepstra, spacing, sampleRate, transpose=False, showColorbar=False)

    ctx.pop()
    pycuda.tools.clear_context_caches()

