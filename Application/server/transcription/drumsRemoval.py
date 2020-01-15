#! /usr/bin/env python

import sys
from os import path
from aubio import onset, source # pylint: disable=no-name-in-module
import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft, ifft
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

def remove_a_from_b():
	raise NotImplementedError()
	#by spectra or amplitude? ? ?

def cross_correlation(inputData, onsets, exampleSounds, sampleRate, frameWidth=4096, sizeOfZeroPadding=4096, spacing=4096):
	zeropad = np.zeros(sizeOfZeroPadding)
	def corr(a, b):
		div = np.linalg.norm(a) * np.linalg.norm(b) #cosine of angle between those two vectors
		fftA = fft(np.concatenate((a, zeropad)))
		fftRevB = fft(list(reversed(np.concatenate((b, zeropad)))))
		crossCorrelation = abs(ifft(fftA * fftRevB))
		return crossCorrelation / div

	possibleEvents = {}
	for onset in onsets:
		currSoundsCorrelations = []
		for sound in exampleSounds:
			currCorrelations = []
			for i in range(0, int(math.ceil((len(sound) - frameWidth) / spacing))):
				if len(inputData) < onset+i*spacing:
					break
				maxDataLen = min(len(sound) - i*spacing, frameWidth, len(inputData) - (onset+i*spacing))
				baseSoundWindow = inputData[(onset+i*spacing):(onset+i*spacing+maxDataLen)]
				testedSoundWindow = sound[(i*spacing):(i*spacing+maxDataLen)]
				correlation = corr(baseSoundWindow, testedSoundWindow)
				currCorrelations.append(max(correlation))
			avg = sum(currCorrelations) / len(currCorrelations)
			print(avg)
			currSoundsCorrelations.append(avg)
		if round(max(currSoundsCorrelations), 1) >= 0.3:
			possibleEvents[onset] = np.argmax(currSoundsCorrelations)
	print(possibleEvents)


if __name__ == "__main__":

	frameWidth = 2048
	spacing = 2048
	filePath = path.dirname(path.abspath(__file__))
	#filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
	#filePath = '../test_sounds/Sine_sequence.wav'
	trackPath = path.join(filePath, '../test_sounds/example/track.wav')
	sampleRate, data = loadNormalizedSoundFIle(trackPath)
	sounds = []
	paths = [
		path.join(filePath, '../test_sounds/example/track_kick.wav'),
		path.join(filePath, '../test_sounds/example/track_snare.wav'),
		path.join(filePath, '../test_sounds/example/track_hihat1.wav'),
		path.join(filePath, '../test_sounds/example/track_hiHat2.wav'),
	]

	for path in paths:
		_, soundData = loadNormalizedSoundFIle(path)
		sounds.append(soundData)
	sampleRate = 44100

	onsets = detect_onsets(trackPath)
	cross_correlation(data, onsets, sounds, sampleRate, frameWidth, frameWidth, spacing)