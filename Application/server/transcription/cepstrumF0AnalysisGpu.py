import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
import math
from utils.general import loadNormalizedSoundFIle, create_sine
from utils.plots import plot_spectrum_line_component_only, plot_spectrum_line_components, plot_spectrogram, plot_cepstrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal
from utils.custom_profile import profile, print_prof_data, print_normalize_profile_data
from utils.cepsUtilsGpu import CepsUtilsGpu
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
from reikna.fft import FFT as gpu_fft
from reikna.cluda import dtypes, cuda_api
from io import BytesIO


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
    #file_path = '../test_sounds/Sine_sequence.wav'
    #filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
    #filePath = path.join(filePath, '../test_sounds/Chopin_prelude28no.4inEm/chopin_prelude_28_4.wav')
    #filePathMain = path.join(filePath, '../test_sounds/EmPiano/Em.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)
    sine_data = create_sine(220, sampleRate, 5)
    sine_data += (create_sine(440, sampleRate, 5) * 0.2)
    sine_data += (create_sine(110, sampleRate, 5) * 0.3)
    
    #GPU
    pycuda.driver.init() # pylint: disable=no-member
    # replace 0 with your device number. In this case, 0 is appropriate
    dev = pycuda.driver.Device(0) # pylint: disable=no-member
    ctx = dev.make_context()
    api = cuda_api()
    thr = api.Thread.create()
    compiledCepstrum = None
    # for i in range(0, 10000):
    cepstra, bestFq, compiledCepstrum = cepstrumF0AnalysisGpu(api, thr, compiledCepstrum, np.array(data), sampleRate, frameWidth, spacing, frameWidth)

    # # plot_pitches(bestFq, spacing, sampleRate)
    plot_cepstrogram(cepstra, spacing, sampleRate, transpose=False, showColorbar=False)
    # plot_pitches(bestFq, spacing, sampleRate)

    ctx.pop()
    pycuda.tools.clear_context_caches()
    # print_prof_data()
    # print_normalize_profile_data(10)

