import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from tqdm import tqdm
from utils.profile import profile, print_prof_data
import skcuda.fft as cu_fft
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
import pyaudio


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
    plan_forward = cu_fft.Plan(data.shape, np.float32, np.complex64 )
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

def create_sine(hz):
    p = pyaudio.PyAudio()
    fs = 44100
    volume = 0.5
    durotian = 55.0
    samples = (np.sin(2*np.pi*np.arange(fs*durotian)*hz/fs)).astype(np.float32)

    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)
    stream.write(volume * samples)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    pycuda.driver.init()
    dev = pycuda.driver.Device(0) # replace n with your device number
    ctx = dev.make_context()

    sample_rate, data = load_normalized_sound_file(file_path)
    count_fft(data)

    #fft_gpu(data)
    fft_gpu(data)
    ctx.pop()
    print_prof_data()


    create_sine(440)
    #print_wave_file(sample_rate, data, file_path.split('/')[-1][:-4])
    pycuda.tools.clear_context_caches()
    #kurwa jego jebana mać 
    
    print("ok")
    
