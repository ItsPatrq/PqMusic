import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
import math
from utils.general import loadNormalizedSoundFIle, create_sine
from utils.plots import plot_spectrum_line_component_only, plot_spectrum_line_components, plot_spectrogram, plot_cepstrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation
from utils.profile import profile, print_prof_data
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal
from pycuda import cumath
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
import pycuda.cumath
from reikna.fft import FFT as gpu_fft
from reikna.cluda import dtypes, cuda_api
from utils.profile import profile, print_prof_data, print_normalize_profile_data
from utils.cepstrumUtilsGpu import Cepstrogram
from io import BytesIO


@profile
def cepstrumF0Analysis (data, sampleRate = 1024, frameWidth = 512, sizeOfZeroPadding = 512, spacing = 512):
    hanning = np.hanning(frameWidth)
    spectrogram = []
    logSpectrogram = []
    cepstra = []
    bestFq = []
    zeroPadding = np.zeros(sizeOfZeroPadding)

    for i in range(0, int(math.ceil((len(data) - frameWidth) / spacing))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hanning
        frame = np.concatenate((frame, zeroPadding))
        cepst, logSp, spectr = real_cepst_from_signal(frame)
        fftLen = int(np.floor(len(spectr)/2))
        spectrogram.append(np.abs(spectr[:fftLen]))
        logSpectrogram.append(logSp[:fftLen])
        cepst = cepst[:fftLen//2]
        cepst[0:14] = np.zeros(14)
        cepstra.append(cepst)
        
        maxperiod = np.argmax(cepst)
        bestFq.append(sampleRate/maxperiod)
    
    return cepstra, spectrogram, bestFq, logSpectrogram

@profile
def ceostrumF0AnalysisGpu (api, thr, data, sampleRate = 1024, frameWidth = 512, sizeOfZeroPadding = 512, spacing = 512, compiledCepstrum=None):
    if compiledCepstrum is None:
        params = dict(Fs=sampleRate, NFFT=frameWidth, noverlap=frameWidth-spacing, pad_to=frameWidth+sizeOfZeroPadding)
        compiledCepstrum = Cepstrogram(
            data, NFFT=params['NFFT'], noverlap=params['noverlap'], pad_to=params['pad_to']).compile(thr)

    data_dev = thr.to_device(data)
    ceps_dev = thr.empty_like(compiledCepstrum.parameter.output)
    compiledCepstrum(ceps_dev, data_dev)
    cepstra = ceps_dev.get()
    # bestFq = []
    # for cepst in cepstra:
    #     maxperiod = np.argmax(cepst)
    #     if maxperiod == 0:
    #         bestFq.append(0)
    #     else:
    #         bestFq.append(sampleRate/maxperiod)
    return cepstra, compiledCepstrum

def transcribe_by_cepstrum_wrapped(filePath):
    frameWidth = 2048
    spacing = 512
    sampleRate, data = loadNormalizedSoundFIle(filePath)
    cepstra, spectra, bestFq, logSpectrogram  = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)

    fig, _ = plot_pitches(bestFq, spacing, sampleRate, show=False, language="pl")
    fig2, _ = plot_cepstrogram(cepstra, spacing, sampleRate, show=False, language="pl")
    fig3, _ = plot_spectrogram(spectra, spacing, sampleRate, show=False, language="pl")
    fig4, _ = plot_spectrogram(logSpectrogram, spacing, sampleRate, show=False, language="pl", title="logPowSpectrogram")


    pitches, cepstrogram, spectrogram, logSpectrogram = BytesIO(), BytesIO(), BytesIO(), BytesIO()
    fig.savefig(pitches, format="png")
    fig2.savefig(cepstrogram, format="png")
    fig3.savefig(spectrogram, format="png")
    fig4.savefig(logSpectrogram, format="png")

    return pitches, cepstrogram, spectrogram, logSpectrogram


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
    
    #for i in range(0, 10):
    cepstra, spectra, bestFq, logSpectrogram = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)
    #---------------------------
    # filePath1 = path.join(filePath, '../test_sounds/EmPiano/E3.wav')
    # sampleRate, data = loadNormalizedSoundFIle(filePath1)

    # cepstra, spectra1, bestFq, logSpectrogram = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)
    # filePath2 = path.join(filePath, '../test_sounds/EmPiano/G3.wav')
    # sampleRate, data = loadNormalizedSoundFIle(filePath2)

    # cepstra, spectra2, bestFq, logSpectrogram = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)
    # filePath3 = path.join(filePath, '../test_sounds/EmPiano/B3.wav')
    # sampleRate, data = loadNormalizedSoundFIle(filePath3)
    # cepstra, spectra3, bestFq, logSpectrogram = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)

    plot_pitches(bestFq, spacing, sampleRate, language='pl')
    # plot_spectrogram(spectra, spacing, sampleRate, language='pl', showColorbar=False)
    # plot_spectrum_line_component_only(spectra[5], sampleRate, language="pl")
    # plot_spectrum_line_components(spectra[5],spectra1[5],spectra2[5],spectra3[5], sampleRate, language="pl")
    # plt.show()
    plot_cepstrogram(cepstra, spacing, sampleRate, language='pl', showColorbar=False)

    #GPU
    pycuda.driver.init() # pylint: disable=no-member
    # replace 0 with your device number. In this case, 0 is appropriate
    dev = pycuda.driver.Device(0) # pylint: disable=no-member
    ctx = dev.make_context()
    api = cuda_api()
    thr = api.Thread.create()
    compiledCepstrum = None
    # for i in range(0, 10000):
    cepstra, compiledCepstrum = ceostrumF0AnalysisGpu(api, thr, np.array(data), sampleRate, frameWidth, frameWidth, spacing, compiledCepstrum)

    # # plot_pitches(bestFq, spacing, sampleRate)
    plot_cepstrogram(cepstra, spacing, sampleRate, transpose=False, showColorbar=False)
    # plot_pitches(bestFq, spacing, sampleRate)

    ctx.pop()
    pycuda.tools.clear_context_caches()
    # print_prof_data()
    # print_normalize_profile_data(10)

