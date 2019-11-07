import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from tqdm import tqdm
from utils.profile import profile, print_prof_data
from pycuda.tools import make_default_context
import skcuda.fft as cu_fft
import pycuda.gpuarray as gpuarray
import pycuda.autoinit
frame_width = 2048
hamming = np.hamming(frame_width)
file_path = './chopin-nocturne.wav'
spacing = 2048
#file_path = './chopin-nocturne.wav'

def toMono(data):
    if len(data.shape) == 2 and data.shape[1] == 2:
        return (data[:, 0]/2 + data[:, 1]/2)
    else:
        return data


def normalize_data(sample_rate, data):
    if(data.dtype == np.int16):
            data_normalization = 2**16
    elif (data.dtype == np.int32):
        data_normalization = 2**32
    else:
        raise Exception("16 and 32 bit audio files only supported")

    mono = toMono(data)

    return np.array(mono) / float(data_normalization)

def print_wave_file(sample_rate, normalized_data, wave_name):
    time_space = np.linspace(0, len(data)/sample_rate, num=len(data))
    plt.figure()
    plt.title("wave " + wave_name)
    plt.xlabel("time (seconds)")
    plt.ylabel("amplitude[-0.5:0.5] (data)")
    plt.yticks(np.arange(-0.5, 0.5, 0.1))
    plt.plot(time_space, normalized_data)
    plt.show()

def load_normalized_sound_file(file_path):
    if file_path.endswith(".wav") == False:
        raise Exception("Only .wav files allowed")

    sample_rate, data = wavfile.read(file_path)
    normalized_data = normalize_data(sample_rate, data)

    return sample_rate, normalized_data

@profile
def fft_gpu(data):
    if data.dtype != ('float32'):
        data = data.astype('float32')

    xgpu = gpuarray.to_gpu(data)
    y = gpuarray.empty(data.shape, np.float32)
    plan_forward = cu_fft.Plan(data.shape // 2 + 1, np.float32, np.float32)
    cu_fft.fft(xgpu, y, plan_forward)

    out = y.get()

    yout = np.hstack(out)
    return yout.astype('float64')



@profile
def count_fft(data):
    spectra = []
    for i in tqdm(range(0, int((len(data) - frame_width) / spacing))):
        frame = (data[i*spacing:i*spacing+frame_width]) * hamming
        spectra.append(fft(frame))
    return spectra

def gpu_example():
    a = np.ones(4000, dtype=np.float32)
    a_gpu = gpuarray.to_gpu(a)
    ans = (2 * a_gpu).get()
    return ans

sample_rate, data = load_normalized_sound_file(file_path)
count_fft(data)
#fft_gpu(data)
gpu_example()
print_prof_data()



#print_wave_file(sample_rate, data, file_path.split('/')[-1][:-4])
print("ok")
