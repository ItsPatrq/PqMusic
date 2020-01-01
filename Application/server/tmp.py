import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
from utils.profile import profile, print_prof_data
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
import pycuda.cumath
import pyaudio
import math
import utils.pqutils as pqutils
from reikna import fft as cu_fft
import cusignal

frame_width = 2048
spacing = 2048
file_path = './test_sounds/Sine_sequence_simplest.wav'
#file_path = './test_sounds/chopin-nocturne.wav'

@profile
def fft_gpu(data):
    xgpu = gpuarray.to_gpu(data)
    hamming_gpu = gpuarray.to_gpu(np.hamming(frameWidth))
    spectra = []
    frame = gpuarray.empty(data[:frame_width].shape, np.complex128)
    plan_forward = cu_fft.Plan(data[:frame_width].shape, np.float64, np.complex128)

    for i in tqdm(range(0, int((len(data) - frame_width) / spacing))):

        cu_fft.fft((xgpu[i * spacing:i*spacing+frame_width] * hamming_gpu), frame, plan_forward)
        spectra.append((pycuda.cumath.log(frame.__abs__())).get()[:(int(np.floor(frame_width/2) - 1))])

    return spectra



@profile
def count_fft(data, frameWidth, spacing):
    hamming = np.hamming(frameWidth)
    spectra = []
    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        frame_complex = fft((data[i*spacing:i*spacing+frameWidth]) * hamming)
        frame_len = int(np.floor(len(frame_complex)/2))
        frame_amplitude = np.log(abs(frame_complex))
        spectra.append(frame_amplitude[:(frame_len - 1)])
    return spectra


@profile
def cepstrogram(data, frameWidth, spacing, sampleRate):
    spectra = []
    cepstrum = []
    bestFq = []
    hamming = np.hamming(frame_width)

    for i in tqdm(range(0, int((len(data)-frameWidth)/spacing))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hamming
        complex_fourier = fft(frame)
        fft_len = int(np.floor(len(complex_fourier)/2))
        power_sp = np.log(abs(complex_fourier))

        spectra.append(power_sp[:(fft_len-1)])

        cepst = abs(fft(power_sp).real)[:fft_len//2]/frameWidth
        cepstrum.append(cepst)
        cepst[0:8] = np.zeros(8)
        maxPeriod = np.argmax(cepst[30:]) + 30
        bestFq.append(sampleRate/maxPeriod)
    
    return spectra, cepstrum, bestFq

@profile
def cepstrogramGPU(data, frameWidth, spacing, sampleRate):
    xgpu = gpuarray.to_gpu(data)
    hamming_gpu = gpuarray.to_gpu(np.hamming(frameWidth))
    spectra = []
    cepstrum = []
    bestFq = []
    frame_complex = gpuarray.empty((frame_width,), np.complex128)
    
    #Dlaczego tutaj ta 1 w shape jest tak bardzo wazna? Bez niej duzo wynikow od konca ma wartosc -inf
    plan_forward = cu_fft.Plan((frame_width,1), np.float64, np.complex128)
    fft_len = int(np.floor(frameWidth/2))
    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        cu_fft.fft((xgpu[i * spacing:i*spacing+frameWidth] * hamming_gpu), frame_complex, plan_forward)
        power_sp = (pycuda.cumath.log(frame_complex.__abs__()))
        spectra.append(power_sp.get()[:fft_len - 1])
        cu_fft.fft(power_sp, frame_complex, plan_forward)
        cepst = frame_complex.real.__abs__().get()[:fft_len//2]/frameWidth
        cepstrum.append(cepst)
        cepst[0:8] = np.zeros(8)
        maxPeriod = np.argmax(cepst[30:]) + 30
        
        bestFq.append(sampleRate/maxPeriod)

    return spectra, cepstrum, bestFq

# Autocorrelation of Log Spectrum https://www.researchgate.net/publication/232643468_Robust_method_of_measurement_of_fundamental_frequency_by_ACLOS_autocorrelation_of_log_spectrum
# + pytanie o użycie grafik
# https://dsp.stackexchange.com/questions/736/how-do-i-implement-cross-correlation-to-prove-two-audio-files-are-similar
def ACLOS(data, frameWidth, spacing, sampleRate):
    # to be exactly as in paper
    frameWidth = 1024
    spacing = 1024
    # 

    correlogram = []
    bestFq = []
    hann = np.hanning(frameWidth)

    def ac(data, minLag, maxLag):
        # w teiri dwie pętle, ale *= leci po wszystkich elementach
        n = len(data)
        result = []
        print(maxLag)
        for lag in range(0, maxLag):
            sumArray = np.zeros(n + lag)
            sumArray[:n] = data
            sumArray[:n-lag] *= data[lag:]
            sum = np.sum(sumArray[:n-lag])
            result.append(float(sum/(n-lag)))

        return result

    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        frame = data[i*spacing:i*spacing+frameWidth] * hann
        assert len(frame) == frameWidth

        frame = np.concatenate([frame, np.zeros(frameWidth)])
        assert len(frame) == frameWidth * 2

        frame_complex = fft(frame)
        frame_amplitude = np.log(abs(frame_complex))
        print(len(frame_amplitude))
        autocorrelation = ac(frame_amplitude, 20, len(frame_amplitude))
        print(len(autocorrelation))
        correlogram.append(autocorrelation)
        bestFq.append(np.argmax(autocorrelation))

    return correlogram, bestFq


# # http://www.ii.uib.no/~espenr/hovedfag/thesis.pdf p 31
# def crossCorelation():
#     autocorr_func_gpu = ...
#     samples = [...]
#     for i in range((0, int((len(data) - frame_width) / spacing))):
#         frame = cpu_fft
        

def gpu_example():
    a = np.ones(4000, dtype=np.float32)
    a_gpu = gpuarray.to_gpu(a)
    ans = (2 * a_gpu).get()
    return ans

def create_sine(hz, sample_rate, durotian):
    samples = np.arange(sample_rate * durotian) / sample_rate
    return  np.sin(2 * np.pi * hz * samples)

    
if __name__ == "__main__":
    frameWidth = 2048
    spacing = 2048


    pycuda.driver.init()
    dev = pycuda.driver.Device(0) # replace n with your device number
    ctx = dev.make_context()

    sample_rate, data = pqutils.loadNormalizedSoundFIle(file_path)

    sine_data = create_sine(440, 44100, 10)
    # fft2 = fft_gpu(sine_data)

    # fft1 = count_fft(sine_data)

    # print("FFT CPU:", len(fft1), fft1[0].shape, fft1[0].dtype, fft1[1] )
    # print("FFT GPU:", len(fft2), fft2[0].shape,fft2[0].dtype, fft2[1])

    # pqutils.plotSpectrogram(fft1, frame_width, spacing, 44100)
    # pqutils.plotSpectrogram(fft2, frame_width, spacing, 44100)

    # spectra, cepstrum, bestFq = cepstrogramGPU(data, frame_width, spacing, sample_rate)

    # pqutils.plotSpectrogram(spectra, frame_width, spacing, 44100)
    # pqutils.plot_correlogram(cepstrum, frame_width, spacing, sample_rate)
    # pqutils.plot_pitches(bestFq, spacing, sample_rate)
   

    # spectra, cepstrum, bestFq = cepstrogram(data, frame_width, spacing, sample_rate)

    # pqutils.plotSpectrogram(spectra, frame_width, spacing, 44100)
    #pqutils.plot_correlogram(cepstrum, frame_width, spacing, sample_rate)
    #pqutils.plot_pitches(bestFq, spacing, sample_rate)

    correlogram, bestFq = ACLOS(data, frame_width, spacing, sample_rate)
    pqutils.plot_correlogram(correlogram, frame_width, spacing, sample_rate)
    pqutils.plot_pitches(bestFq, spacing, sample_rate)
    

    ctx.pop()
    print_prof_data()

    #pqutils.printWave(sample_rate, data, file_path.split('/')[-1][:-4])
    pycuda.tools.clear_context_caches()
    
    print("ok")
    
