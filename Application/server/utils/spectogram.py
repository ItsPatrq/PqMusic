import os
import wave
from  .general import convertAudioFileToWave, path_leaf
import pylab

def graph_spectrogram(file_name, result_path):
    sound_info, frame_rate = get_file_info(file_name)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('Spektogram of %r' % path_leaf(file_name))
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig(result_path)

def get_file_info(file_name):
    waveFilePath = convertAudioFileToWave(file_name)
    wav = wave.open(waveFilePath, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate

if __name__ == '__main__':
    file_name = './spectogram/Violas.mp3'
    graph_spectrogram(file_name, '.')