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
import pycuda.cumath
import pyaudio
import math

def fourier_to_hz(freq, fw, br):
  return freq*br/fw

def hz_to_fourier(freq, fw, br):
  return int(np.round(freq*fw/br))
# common display resources

freqlabels_log = [50, 100, 200, 400, 800, 1600, 3200, 6000]

def freqticks_log(fw, br):
  ticks = []
  for f in freqlabels_log:
    ticks.append(hz_to_fourier(f, fw, br))
  return ticks

freqlabels = [400, 800, 1600, 2400, 3200, 4800, 6000]

def freqticks(fw, br, upper_bound = 0):
  ticks = []
  for f in freqlabels:
    k = hz_to_fourier(f, fw, br)
    if upper_bound > 0 and k > upper_bound:
      break
    ticks.append(k)
  return ticks

seclabels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

def periodticks(br=44100):
  ticks = []
  for f in freqlabels_log:
    ticks.append(br/f)
  return ticks

def secticks(fw, br):
  ticks = []
  for t in seclabels:
    ticks.append(fourier_to_hz(t, fw, br))
  return ticks

notelabels = ["C2", "G2", "C3", "G3", "C4", "G4", "C5", "G5", "C6", "G6"]
noteticks  = [36, 43, 48, 55, 60, 67, 72, 79, 84, 91]

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
    time_space = np.linspace(0, len(normalized_data)/sample_rate, num=len(normalized_data))
    plt.figure()
    plt.title("wave " + wave_name)
    plt.xlabel("time (seconds)")
    plt.ylabel("amplitude[" + str(math.floor(normalized_data.min())) + ":" + str(math.ceil(normalized_data.max())) +"] (data)")
    plt.yticks(np.arange(math.floor(normalized_data.min()), math.ceil(normalized_data.max()), 0.1))
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
    xgpu = gpuarray.to_gpu(data)
    spectra = []

    for i in tqdm(range(0, int((len(data) - frame_width) / spacing))):
        frame = gpuarray.empty(data[:frame_width].shape, np.complex128)
        plan_forward = cu_fft.Plan(data[:frame_width].shape, np.float64, np.complex128 )
        cu_fft.fft(xgpu[i * spacing:i*spacing+frame_width], frame, plan_forward)
        spectra.append((pycuda.cumath.log(frame.__abs__())).get()[:(int(np.floor(frame_width/2)))])

    return spectra



@profile
def count_fft(data):
    spectra = []
    for i in tqdm(range(0, int((len(data) - frame_width) / spacing))):
        frame_complex = fft((data[i*spacing:i*spacing+frame_width]) * hamming)
        frame_len = int(np.floor(len(frame_complex)/2))
        frame_amplitude = np.log(abs(frame_complex))
        spectra.append(frame_amplitude[:(frame_len - 1)])
    return spectra

def gpu_example():
    a = np.ones(4000, dtype=np.float32)
    a_gpu = gpuarray.to_gpu(a)
    ans = (2 * a_gpu).get()
    return ans

def create_sine(hz, sample_rate, durotian):
    samples = np.arange(sample_rate * durotian) / sample_rate
    return  np.sin(2 * np.pi * hz * samples)

def to_wave(signal, frame_rate, name):
    signal = signal * 32767
    signal = np.int16(signal)
    wavfile.write(name + ".wav", frame_rate, signal)


def plot_spectrogram(spectra, fw, spacing, br, upper_bound=0):
    H = np.array(spectra)
    if upper_bound > 0:
        plt.imshow(H.T[:upper_bound], origin='lower',
                aspect='auto', interpolation='nearest')
        plt.yscale('log')
        plt.yticks(freqticks(fw, br, upper_bound), freqlabels)
    else:
        plt.imshow(H.T, origin='lower', aspect='auto', interpolation='nearest')
        plt.yscale('log')
        plt.yticks(freqticks(fw, br), freqlabels)
    plt.ylabel('frequency (Hz)')

    plt.xlabel('time (seconds)')
    sec_length = int(len(spectra)*spacing/br)
    plt.xticks(secticks(spacing, br)[:sec_length], seclabels[:sec_length])
    plt.show()


    
if __name__ == "__main__":
    pycuda.driver.init()
    dev = pycuda.driver.Device(0) # replace n with your device number
    ctx = dev.make_context()

    sample_rate, data = load_normalized_sound_file(file_path)

    sine_data = create_sine(440, 44100, 20)
    fft2 = fft_gpu(sine_data)

    fft1 = count_fft(sine_data)

    print("FFT CPU:", len(fft1), fft1[0].shape, fft1[0].dtype, fft1[1] )
    print("FFT GPU:", len(fft2), fft2[0].shape,fft2[0].dtype, fft2[1])

    plot_spectrogram(fft1, frame_width, spacing, sample_rate)
    plot_spectrogram(fft2, frame_width, spacing, sample_rate)

    ctx.pop()
    print_prof_data()

    #print_wave_file(sample_rate, data, file_path.split('/')[-1][:-4])
    pycuda.tools.clear_context_caches()
    
    print("ok")
    
