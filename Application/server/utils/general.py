## W tym pliku znajdują się ogólne funkcje pomocznicze

from pydub import AudioSegment
import ntpath
import numpy as np
from scipy.io import wavfile
import heapq

ntpath.basename("a/b/c")

def fourier_to_hz(freq, frameWidth, bitRate):
  return freq*bitRate/frameWidth


def hz_to_fourier(freq, frameWidth, bitRate):
  return int(np.round(freq*frameWidth/bitRate))

def convertAudioFileToWave(file_path):
  if file_path.endswith(".mp3"):
    mp3 = AudioSegment.from_mp3(file_path)
    file_path = file_path[:-3] + "wav"
    mp3.export(file_path, format="wav")

  if file_path.endswith(".wav"):
    return file_path

  exception = BaseException("File extension not supported")
  raise exception


def to_wave(signal, frame_rate, name):
    signal = signal * 32767
    signal = np.int16(signal)
    wavfile.write(name + ".wav", frame_rate, signal)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def toMono(data):
  if len(data.shape) == 2 and data.shape[1] == 2:
    return (data[:, 0]/2 + data[:, 1]/2)
  else:
    return data


def normalizeData(sample_rate, data):
  if(data.dtype == np.int16):
    dataNormalization = 2**16
  elif (data.dtype == np.int32):
    dataNormalization = 2**32
  else:
    raise Exception("Received " + str(data.dtype) +
                    " dtype while 16 and 32 bit audio files only supported")

  mono = toMono(data)

  return np.array(mono) / float(dataNormalization)


def loadNormalizedSoundFile(file_path):
  file_path = convertAudioFileToWave(file_path)
  if file_path.endswith(".wav") == False:
    raise Exception("Only .wav files allowed")

  sampleRate, data = wavfile.read(file_path)
  normalizedData = normalizeData(sampleRate, data)

  return sampleRate, normalizedData



def fft_to_hz(sampleRate, numberOfSamples):
  return (sampleRate / 2) * np.linspace(0, 1, numberOfSamples)

def hz_to_fft(sampleRate, numberOfSamples):
  halfSR = sampleRate // 2 + 1 if sampleRate % 2 == 1 else sampleRate // 2
  return np.arange(0, halfSR) * numberOfSamples / (sampleRate / 2)

def create_sine(hz, sample_rate, durotian):
  samples = np.arange(sample_rate * durotian) / sample_rate
  return np.sin(2 * np.pi * hz * samples)

def get_arg_max(array):
  a = np.array(array)
  return heapq.nlargest(len(array), range(len(a)), a.take)