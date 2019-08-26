import os
import wave

import pylab
from pydub import AudioSegment

def graph_spectrogram(file_name):
    sound_info, frame_rate = get_file_info(file_name)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % file_name)
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.png')
def get_file_info(file_name):
    if file_name.endswith(".mp3"):
        mp3 = AudioSegment.from_mp3(file_name)
        file_name = file_name[:-3] + "wav"
        mp3.export(file_name, format="wav")

    wav = wave.open(file_name, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate
if __name__ == '__main__':
    file_name = './all_of_me.mp3'
    graph_spectrogram(file_name)