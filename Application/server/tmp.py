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
from reikna import fft as cu_fft
from reikna.cluda import dtypes, cuda_api
from utils.plots import plot_spectrogram
from utils.cepstrumUtilsGpu import CepstrumUtilsGpu

@profile
def fft_gpu2(data, frameWidth = 512, spacing = 512):
    api = cuda_api()
    thr = api.Thread.create()

    data_dev = thr.to_device(data)
    hamming_dev = thr.to_device(np.hamming(frameWidth))
    res_dev = thr.empty_like(data_dev[:frameWidth])

    fft = cu_fft.FFT(res_dev)
    fft_compiled = fft.compile(thr)

    spectra = []

    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        fft_compiled(res_dev, data_dev[i * spacing:i*spacing+frameWidth] * hamming_dev, inverse=0)
        result = res_dev.__abs__().get()
        spectra.append(result[:(frameWidth // 2)])

    return spectra


@profile
def count_fft(data, frameWidth, spacing):
    hamming = np.hamming(frameWidth)
    spectra = []
    print(data)
    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        frame_complex = fft((data[i*spacing:i*spacing+frameWidth]) * hamming)
        frame_len = int(np.floor(len(frame_complex)/2))
        frame_amplitude = abs(frame_complex)
        spectra.append(frame_amplitude[:(frame_len - 1)])
    return spectra


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
    sampleRate = 44100
    file_path = './test_sounds/Sine_sequence_simplest.wav'
    #file_path = './test_sounds/chopin-nocturne.wav'

    pycuda.driver.init()
    dev = pycuda.driver.Device(0) # replace n with your device number
    ctx = dev.make_context()
    #cepstrogramGPU = CepstrumUtilsGpu(cuda_api(), frameWidth)

    sine_data = create_sine(220, sampleRate, 10)

    res = cepstrogramGPU.real_cepst_from_signal(sine_data[:frameWidth])
    print(res)
    ctx.pop()
    pycuda.tools.clear_context_caches()
    
    print_prof_data()
    
