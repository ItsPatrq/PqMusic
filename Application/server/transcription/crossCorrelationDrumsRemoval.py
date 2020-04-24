#! /usr/bin/env python

import sys
from os import path
from aubio import onset, source # pylint: disable=no-name-in-module
import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft, ifft
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.general import loadNormalizedSoundFile, create_sine, fft_to_hz, hz_to_fft, hz_to_fourier, to_wave

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


def spectral_removal(inputData, soundToBeRemoved, occurances, sampleRate, frameWidth=4096, sizeOfZeroPadding=4096):
	copiedData = np.array(inputData)
	zeropad = np.zeros(sizeOfZeroPadding)

	def remove_a_from_b(a, b):
		fftA = fft(np.concatenate((a, zeropad)))
		fftB = fft(np.concatenate((b, zeropad)))
		fftA -= fftB.real
		return ifft(fftA).real[:len(a)]

	for occurance in occurances:
		for i in range(0, int(math.ceil((len(soundToBeRemoved) - frameWidth) / frameWidth))):
			if len(copiedData) < occurance+i*frameWidth:
				break
			maxDataLen = min(len(soundToBeRemoved) - i*frameWidth, frameWidth, len(copiedData) - (occurance+i*frameWidth))
			baseSoundWindow = copiedData[(occurance+i*frameWidth):(occurance+i*frameWidth+maxDataLen)]
			removedSoundWindow = soundToBeRemoved[(i*frameWidth):(i*frameWidth+maxDataLen)]
			removed = remove_a_from_b(baseSoundWindow, removedSoundWindow)
			copiedData[(occurance+i*frameWidth):(occurance+i*frameWidth+maxDataLen)] = removed
	
	return copiedData

def cross_correlation(inputData, onsets, exampleSounds, sampleRate, frameWidth=4096, sizeOfZeroPadding=4096, spacing=4096, onsetMissplace=10):
	zeropad = np.zeros(sizeOfZeroPadding)
	def corr(a, b):
		div = np.linalg.norm(a) * np.linalg.norm(b) #cosine of angle between those two vectors
		fftA = fft(np.concatenate((a, zeropad)))
		fftRevB = fft(list(reversed(np.concatenate((b, zeropad)))))
		crossCorrelation = abs(ifft(fftA * fftRevB))
		return crossCorrelation / div

	possibleEvents = {}
	for onset in tqdm(onsets):
		currSoundsCorrelations = []
		for soundIndex, sound in enumerate(exampleSounds):
			currCorrelations = []
			for shiftedOnset in range(max(onset-onsetMissplace, 0), min(onset+onsetMissplace, len(inputData))):
				for i in range(0, int(math.ceil((len(sound) - frameWidth) / spacing))):
					if len(inputData) < shiftedOnset+i*spacing:
						break
					maxDataLen = min(len(sound) - i*spacing, frameWidth, len(inputData) - (shiftedOnset+i*spacing))
					baseSoundWindow = inputData[(shiftedOnset+i*spacing):(shiftedOnset+i*spacing+maxDataLen)]
					testedSoundWindow = sound[(i*spacing):(i*spacing+maxDataLen)]
					correlation = corr(baseSoundWindow, testedSoundWindow)
					currCorrelations.append(max(correlation))
				avg = sum(currCorrelations) / len(currCorrelations)
				currSoundsCorrelations.append((avg, soundIndex))
		maxElement = np.argmax(np.array(currSoundsCorrelations).T[0]) #pylint: disable=unsubscriptable-object
		if round(currSoundsCorrelations[maxElement][0], 1) >= 0.3:
			possibleEvents[onset] = currSoundsCorrelations[maxElement][1]
	return possibleEvents

def drums_removal_example():
	frameWidth = 2048
	spacing = 512
	filePath = path.dirname(path.abspath(__file__))
	trackPath = path.join(filePath, '../test_sounds/example/track.wav')
	sampleRate, data = loadNormalizedSoundFile(trackPath)
	sounds = []
	paths = [
		path.join(filePath, '../test_sounds/example/track_kick.wav'),
		path.join(filePath, '../test_sounds/example/track_snare.wav'),
		path.join(filePath, '../test_sounds/example/track_hihat1.wav'),
		path.join(filePath, '../test_sounds/example/track_hiHat2.wav'),
	]

	for currPath in paths:
		_, soundData = loadNormalizedSoundFile(currPath)
		sounds.append(soundData)
	sampleRate = 44100
	onsets = detect_onsets(trackPath)
	res1 = cross_correlation(data, onsets, sounds, sampleRate, frameWidth, frameWidth, spacing)
	occurances = []
	while len(occurances) < len(sounds):
		occurances.append([])
	for key, value in res1.items():
		occurances[value].append(key)
	
	for i in range(0, len(sounds)):
		res = spectral_removal(data, sounds[i], occurances[i], sampleRate)
	to_wave(res, sampleRate, "costam.wav")

if __name__ == "__main__":
	drums_removal_example()