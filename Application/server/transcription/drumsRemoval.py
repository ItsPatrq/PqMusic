#! /usr/bin/env python

import sys
from os import path
from aubio import onset, source
from numpy import hstack, zeros
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from utils.general import loadNormalizedSoundFIle, create_sine, fft_to_hz, hz_to_fft, hz_to_fourier

# right now using aubio library, might implement own later
def detect_onsets(filePath, method="default", windowSize=1024):
	hop_s = windowSize // 2
	s = source(filePath, hop_size=hop_s)
	samplerate = s.samplerate

	o = onset("default", windowSize, hop_s, samplerate)

	# list of onsets, in samples
	onsets = []

	# total number of frames read
	total_frames = 0
	while True:
		samples, read = s()
		if o(samples):
			onsets.append(o.get_last())
		total_frames += read
		if read < hop_s: break
	return onsets



if __name__ == "__main__":

	frameWidth = 8192
	spacing = 1024
	filePath = path.dirname(path.abspath(__file__))
	#filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
	#filePath = '../test_sounds/Sine_sequence.wav'
	filePath = path.join(filePath, '../test_sounds/areFE.wav')
	sampleRate, data = loadNormalizedSoundFIle(filePath)
	sampleRate = 44100

	onsets = detect_onsets(filePath)
	print(onsets)