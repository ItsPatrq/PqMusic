import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import sys
from copy import deepcopy
from os import path
from itertools import combinations
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.cepstrumUtils import real_cepst_from_signal
from scipy.interpolate import interp1d
from utils.profile import profile, print_prof_data
from utils.plots import plot_spectrogram, plot_pitches, plot_midi, plot_peaks
from utils.general import loadNormalizedSoundFIle, create_sine, fft_to_hz, hz_to_fft, hz_to_fourier
from utils.midi import write_midi, hz_to_midi, midi_to_hz, MidiNote

def harmonicAndSmoothnessBasedTranscription(data, sampleRate=1024, frameWidth=512, sizeOfZeroPadding=512, spacing=512,
                                            minF0=75, maxF0=4000, peakDistance=2, relevantPowerThreashold=8, maxInharmonyDegree=0.1, minHarmonicsPerCandidate=2,
											maxHarmonicsPerCandidate=20, maxCandidates=10, maxParallelNotes = 6, gamma=0.1, minNoteMs=100):

	#region init values
	hann = np.hanning(frameWidth)
	resF0Weights = []
	resNotes = []
	zeropad = np.zeros(sizeOfZeroPadding)
	gaussianPoints = [0.21, 0.58, 0.21]
	fftLen = int(np.floor((frameWidth + sizeOfZeroPadding)/2))

	fft_to_hz_array = fft_to_hz(sampleRate, fftLen)
	hz_to_fft_array = hz_to_fft(sampleRate, frameWidth*2)

	k0 = int(np.round(hz_to_fft_array[minF0]))
	k1 = int(np.round(hz_to_fft_array[maxF0]))

	maxMidiPitch = hz_to_midi(maxF0) + 1
	#endregion init values

	def countMaxInharmonyFrequencies(expectedFft):
		expectedFq = fft_to_hz_array[expectedFft]
		currNote = hz_to_midi(expectedFq)
		currNoteFq = midi_to_hz(currNote)
		prevNoteFq = midi_to_hz(currNote - 1)
		nextNoteFq = midi_to_hz(currNote + 1)
		return int(np.round((currNoteFq - prevNoteFq) * maxInharmonyDegree)), int(np.round((nextNoteFq - currNoteFq) * maxInharmonyDegree))

	def getCandidatesThatHaveEnoughHarmonics(candidate, peaks):
		hypotheses = []
		amplitudeSum = np.zeros(k1)
		patterns = {}
		ownerships = {}
		for f0Candidate in candidate:
			harmonicsFound = 0
			currAmplitudeSum = np.array(amplitudeSum)
			currPatterns = deepcopy(patterns)
			currOwnerships = deepcopy(ownerships)
			currAmplitudeSum[f0Candidate] = peaks[f0Candidate]
			currPatterns[f0Candidate] = [(f0Candidate, peaks[f0Candidate])]
			for harmonic in range(2, maxHarmonicsPerCandidate):
				currExpHarFft = harmonic * f0Candidate
				if currExpHarFft > len(peaks) - 1:
					break
				maxLeftInh, maxRightInh = countMaxInharmonyFrequencies(currExpHarFft)
				maxCurrHarmonic = min(len(peaks) - 1, int(currExpHarFft + maxRightInh))
				bestFq = np.argmax(peaks[(currExpHarFft - maxLeftInh):maxCurrHarmonic]) + currExpHarFft - maxLeftInh
				bestPow = peaks[bestFq]
				if bestPow > 0:
					harmonicsFound += 1
					if bestFq in currOwnerships:
						currOwnerships[bestFq].append(f0Candidate)
					else:
						currOwnerships[bestFq] = [f0Candidate]
					currAmplitudeSum[f0Candidate] += bestPow
					currPatterns[f0Candidate].append((bestFq, bestPow))
			if harmonicsFound >= minHarmonicsPerCandidate:
				hypotheses.append(f0Candidate)
				amplitudeSum = currAmplitudeSum
				patterns = currPatterns
				ownerships = currOwnerships
		return hypotheses, amplitudeSum, patterns, ownerships

	def updateMinMaxL(loudness, highestLoudness, lowestLoudness):
		if highestLoudness is None or highestLoudness < loudness:
			highestLoudness = loudness
		if lowestLoudness is None or lowestLoudness > loudness:
			lowestLoudness = loudness
		return highestLoudness, lowestLoudness

	def countPowerFftWindow(i):
		frame = data[i*spacing:i*spacing+frameWidth] * hann
		frame = np.concatenate((frame, zeropad))
		frameComplex = fft(frame)
		return abs(frameComplex)[:fftLen]

	def getPeaksAndCandidates(powerSpWindow):
		peaks = np.zeros(len(powerSpWindow))
		candidate = []

		for k in range(1, len(powerSpWindow)-1):
			currPower = powerSpWindow[k]
			if currPower > relevantPowerThreashold and np.argmax(powerSpWindow[k-peakDistance:k+peakDistance+1]) + k-peakDistance == k:
				peaks[k] = currPower
				if k > k0 and k < k1:
					candidate.append(k)

		return peaks, candidate

	def getMaxCandidatesByPower(amplitudeSum, hypotheses):
		sortedByPow = []
		cpAmplitudeSum = np.array(amplitudeSum)
		for _ in list(amplitudeSum.nonzero()[0]):
			maxFq = np.argmax(cpAmplitudeSum)
			if maxFq == 0:
				break
			cpAmplitudeSum[maxFq] = 0
			if maxFq in hypotheses:
				sortedByPow.append(maxFq)

		sortedByPow = sortedByPow[:maxCandidates]
		return np.sort(sortedByPow)

	def countCombinationSalience(combination, patterns, peaks):
		currPatterns = deepcopy(patterns)
		currPeaks = np.array(peaks)
		combinationSalience = 0
		highestLoudness = None
		lowestLoudness = None
		for fundamental in combination:
			currPattern = currPatterns[fundamental]
			patternHarmonicsToDelete = []

			for harmonic in range(1, len(currPattern)):					
				currHarmonicFft = currPattern[harmonic][0]
				if currPeaks[currHarmonicFft] == 0: #it was taken by other harmonic due to shared pattern
					patternHarmonicsToDelete.append(harmonic)
				elif len(ownerships[currHarmonicFft]) > 1: #shared harmonic
					if len(currPattern) == harmonic + 1:
						if len(currPattern) > 2:
							interpolatedPitch = currPattern[harmonic - 1][1] - ((currPattern[harmonic - 2][1] - currPattern[harmonic - 1][1]) / 2)
						else:
							interpolatedPitch = currPeaks[currPattern[harmonic][0]]
					else:
						interpolatedPitch = (currPattern[harmonic - 1][1] + currPeaks[currPattern[harmonic + 1][0]]) / 2
					if interpolatedPitch > currPeaks[currHarmonicFft]:
						currPattern[harmonic] = (currHarmonicFft, currPeaks[currHarmonicFft])
						currPeaks[currHarmonicFft] = 0
					else: 
						currPattern[harmonic] = (currHarmonicFft, interpolatedPitch)
						currPeaks[currHarmonicFft] -= interpolatedPitch
				else: #non-shared harmonic
					currPattern[harmonic] = (currHarmonicFft, currPeaks[currHarmonicFft])
					currPeaks[currHarmonicFft] = 0
			for i in range(-1, -(len(patternHarmonicsToDelete) + 1), -1):
				del currPattern[patternHarmonicsToDelete[i]]
				
			currPatternPowers = np.array(currPattern)
			currPatternPowers = currPatternPowers.T[1]
			totalPatternLoudness = np.sum(currPatternPowers)
			highestLoudness, lowestLoudness = updateMinMaxL(totalPatternLoudness, highestLoudness, lowestLoudness)
			if(len(currPatternPowers) > 2):
				lowPassedConv = np.convolve(currPatternPowers, gaussianPoints, 'same')
				currPatternSharpnessMeasure = np.sum(abs(lowPassedConv - currPatternPowers)) / len(currPatternPowers)
			else:
				currPatternSharpnessMeasure = 0 # only possible if minHarmonicsPerCandidate set to less then 2
			currPatternSmoothness = 1 - currPatternSharpnessMeasure
			combinationSalience += (totalPatternLoudness * currPatternSmoothness) ** 2
		if lowestLoudness < highestLoudness * gamma:
			combinationSalience = 0.0
		return combinationSalience 

	def postProcessMidiNotes(resNotes):
		resultPianoRoll = []
		for i in range(0, len(resNotes)):
			pianoRollRow = np.zeros(maxMidiPitch)
			for notePitch, amplitude in resNotes[i].items():
				amplitude = min(np.round(amplitude * 1.8), 127)
				if i >= 1 and i+1 < len(resNotes):
					if notePitch+1 in resNotes[i-1] and notePitch+1 in resNotes[i+1]:
						pianoRollRow[notePitch+1] = amplitude
					elif notePitch-1 in resNotes[i-1] and notePitch - 1 in resNotes[i+1]:
						pianoRollRow[notePitch-1] = amplitude
					else:
						pianoRollRow[notePitch] = amplitude
				else:
					pianoRollRow[notePitch] = amplitude
			resultPianoRoll.append(pianoRollRow)

		resultNotes = []
		noteTail = minNoteMs / 1000
		for note in range(0, maxMidiPitch):
			currDurotian = 0
			currVelocity = 0
			for i in range(0, len(resultPianoRoll)):
				if resultPianoRoll[i][note] != 0 or\
					(((i - 1 > 0 and resultPianoRoll[i - 1][note] != 0) or (i - 2 > 0 and resultPianoRoll[i - 2][note] != 0) or (i - 3 > 0 and resultPianoRoll[i - 3][note] != 0) or (i - 4 > 0 and resultPianoRoll[i - 4][note] != 0)) and\
					((len(resultPianoRoll) > i + 1 and resultPianoRoll[i + 1][note] != 0) or (len(resultPianoRoll) > i + 2 and resultPianoRoll[i + 2][note] != 0) or (len(resultPianoRoll) > i + 3 and resultPianoRoll[i + 3][note] != 0) or (len(resultPianoRoll) > i + 4 and resultPianoRoll[i + 4][note] != 0))):					
					if resultPianoRoll[i][note] == 0:
						averageVelocity = currVelocity / max(currDurotian, 1)
						currVelocity += averageVelocity
						resultPianoRoll[i][note] = averageVelocity
					else:
						currVelocity += resultPianoRoll[i][note]
					currDurotian += 1
				elif (currDurotian * spacing / sampleRate) * 1000 > minNoteMs:
					onsetIdx = i - currDurotian
					currVelocity /= currDurotian
					currDurotianMs = currDurotian * spacing / sampleRate + noteTail
					resultNotes.append(MidiNote(note, currVelocity, onsetIdx * spacing / sampleRate, currDurotianMs))
					currDurotian = 0
					currVelocity = 0
				else:
					currDurotian = 0
					currVelocity = 0


		return resultNotes, resultPianoRoll


	for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing)))):
		peaks, candidate = getPeaksAndCandidates(countPowerFftWindow(i))

		hypotheses, amplitudeSum, patterns, ownerships = getCandidatesThatHaveEnoughHarmonics(candidate, peaks)
		if(len(hypotheses) == 0):
			resNotes.append({})
			continue

		sortedByFq = getMaxCandidatesByPower(amplitudeSum, hypotheses)

		possibleCombinations = []
		for num_pitches in range(1, min(maxParallelNotes, len(sortedByFq)) + 1):
			for combo in combinations(sortedByFq, num_pitches):
				possibleCombinations.append(combo)

		allSaliences = []
		for combination in possibleCombinations:
			combinationSalience = countCombinationSalience(combination, patterns, peaks)
			allSaliences.append(combinationSalience)

		bestCombination = possibleCombinations[np.argmax(allSaliences)]

		result = np.zeros(k1)
		midiNotes = {}
		for fftFq in bestCombination:
			fq = fft_to_hz_array[fftFq]
			midiNotes[hz_to_midi(fq)] = (amplitudeSum[fftFq] / len(patterns[fftFq]))
			result[fftFq] = amplitudeSum[fftFq]
		resF0Weights.append(result)
		resNotes.append(midiNotes)

	resMidi, resPianoRoll = postProcessMidiNotes(resNotes)

	return resMidi, resPianoRoll, resF0Weights, peaks


if __name__ == "__main__":

	frameWidth = 8192
	spacing = 1024
	filePath = path.dirname(path.abspath(__file__))
	filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
	#file_path = '../test_sounds/Sine_sequence.wav'
	#filePath = path.join(filePath, '../test_sounds/areFE.wav')
	sampleRate, data = loadNormalizedSoundFIle(filePath)
	sampleRate = 44100

	sine_data = create_sine(220, sampleRate, 5)
	sine_data += (create_sine(440, sampleRate, 5) * 0.2)
	sine_data += (create_sine(110, sampleRate, 5) * 0.3)

	resMidi, resPianoRoll, resF0Weights, peaks = harmonicAndSmoothnessBasedTranscription(
            data, sampleRate, frameWidth, frameWidth * 3, spacing)

	#plot_pitches(best_frequencies, spacing, sampleRate)
	#plot_spectrogram(all_weights, spacing, sampleRate)

	write_midi(resMidi, "./res.mid", spacing/sampleRate, 4)
	plot_midi(resPianoRoll, spacing, sampleRate)
	plot_peaks(peaks, frameWidth, sampleRate)
	plot_spectrogram(resF0Weights, spacing, sampleRate)
	print("ok")
