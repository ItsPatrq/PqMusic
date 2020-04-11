import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
from copy import deepcopy
from os import path
from itertools import combinations
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.cepstrumUtils import lifterOnPowerSpec, LifterType
from scipy.interpolate import interp1d
from utils.plots import plot_spectrogram, plot_pitches, plot_midi, plot_peaks, plot_pitch_tracking
from utils.general import loadNormalizedSoundFIle, create_sine, fft_to_hz, hz_to_fft, hz_to_fourier, get_arg_max
from utils.midi import write_midi, hz_to_midi, midi_to_hz, MidiNote, get_midi_bytes, post_process_midi_notes as utilpost_process_midi_notes
import networkx as nx
from collections import namedtuple
import functools 
from io import BytesIO

def harmonic_and_smoothness_based_transcription(data, sampleRate, frameWidth=8192, spacing=1024, sizeOfZeroPadding=24576,
                                            minF0=85, maxF0=5500, peakDistance=8, relevantPowerThreashold=4, maxInharmonyDegree=0.08, minHarmonicsPerCandidate=2,
											maxHarmonicsPerCandidate=10, maxCandidates=8, maxParallelNotes = 5, gamma=0.05, minNoteMs=70,
											useLiftering = True, lifteringCoefficient = 8, minNoteVelocity = 10,
											newAlgorithmVersion=True, smoothnessImportance=3, temporalSmoothnessRange=2, pitch_tracking_combinations=3):

	#region init values
	hann = np.hanning(frameWidth)
	resF0Weights = []
	resNotes = []
	allCombinations = []
	zeropad = np.zeros(sizeOfZeroPadding)
	gaussianPoints = [0.21, 0.58, 0.21]
	fftLen = int(np.floor((frameWidth + sizeOfZeroPadding)/2))

	fft_to_hz_array = fft_to_hz(sampleRate, fftLen)
	hz_to_fft_array = hz_to_fft(sampleRate, frameWidth*2)

	k0 = int(np.round(hz_to_fft_array[minF0]))
	k1 = int(np.round(hz_to_fft_array[maxF0]))

	maxMidiPitch = 127
	CombinationData = namedtuple('CombinationData', "possibleCombinations allSaliences allMidiNotes allResults allPatterns")
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
		powerSpWindow = abs(frameComplex)
		if useLiftering:
			return lifterOnPowerSpec(powerSpWindow, LifterType.sine, lifteringCoefficient)[:fftLen]
		else:
			return powerSpWindow[:fftLen]

	def getPeaksAndCandidates(powerSpWindow):
		peaks = np.zeros(len(powerSpWindow))
		candidate = []

		for k in range(1, len(powerSpWindow)-1):
			currPower = powerSpWindow[k]
			if currPower > relevantPowerThreashold and np.argmax(powerSpWindow[max(k-peakDistance, 0):k+peakDistance+1]) + k-peakDistance == k:
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

	def smoothenPattern(currPattern, currPeaks, ownerships):
		patternHarmonicsToDelete = []

		for harmonic in range(1, len(currPattern)):					
			currHarmonicFft = currPattern[harmonic][0]
			if currPeaks[currHarmonicFft] == 0: #it was taken by other harmonic due to shared pattern
				patternHarmonicsToDelete.append(harmonic)
			elif len(ownerships[currHarmonicFft]) > 1: #shared harmonic
				if len(currPattern) == harmonic + 1:
					if len(currPattern) > 2:
						interpolatedPitch = max(currPattern[harmonic - 1][1] - ((currPattern[harmonic - 2][1] - currPattern[harmonic - 1][1]) / 2), 0)
					else:
						interpolatedPitch = currPeaks[currPattern[harmonic][0]]
				else:
					interpolatedPitch = (currPattern[harmonic - 1][1] + currPeaks[currPattern[harmonic + 1][0]]) / 2
				if interpolatedPitch > currPeaks[currHarmonicFft]:
					currPattern[harmonic] = (currHarmonicFft, currPeaks[currHarmonicFft])
					currPeaks[currHarmonicFft] = 0
				else:
					currPattern[harmonic] = (currHarmonicFft, interpolatedPitch)
					currPeaks[currHarmonicFft] =  max(currPeaks[currHarmonicFft] - interpolatedPitch, 0)
			else: #non-shared harmonic
				currPattern[harmonic] = (currHarmonicFft, currPeaks[currHarmonicFft])
				currPeaks[currHarmonicFft] = 0
		for i in range(-1, -(len(patternHarmonicsToDelete) + 1), -1):
			del currPattern[patternHarmonicsToDelete[i]]
		return currPattern, currPeaks

	def countCombinationSalience(combination, patterns, peaks, ownerships):
		currPatterns = deepcopy(patterns)
		currPeaks = np.array(peaks)
		combinationSalience = 0
		highestLoudness = None
		lowestLoudness = None
		for fundamental in combination:
			currPattern, currPeaks = smoothenPattern(currPatterns[fundamental], currPeaks, ownerships)
				
			currPatternPowers = np.array(currPattern)
			currPatternPowers = currPatternPowers.T[1] # pylint: disable=unsubscriptable-object
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

	def countCombinationSalience2(combination, patterns, peaks, ownerships):
		currPatterns = deepcopy(patterns)
		currPeaks = np.array(peaks)
		combinationSalience = 0
		highestLoudness = None
		lowestLoudness = None
		harmonicsPatterns = []
		for fundamental in combination:
			currPattern, currPeaks = smoothenPattern(currPatterns[fundamental], currPeaks, ownerships)
			harmonicsPatterns.append((hz_to_midi(fft_to_hz_array[fundamental]), currPattern))
					
			currPatternPowers = np.array(currPattern)
			currPatternPowers = currPatternPowers.T[1] # pylint: disable=unsubscriptable-object
			totalPatternLoudness = np.sum(currPatternPowers)
			highestLoudness, lowestLoudness = updateMinMaxL(totalPatternLoudness, highestLoudness, lowestLoudness)
			if lowestLoudness < highestLoudness * gamma:
				return 0.0, harmonicsPatterns

			normalizedHpsPowers = np.array(currPatternPowers) / np.max(currPatternPowers)
			if(len(currPatternPowers) > 2):
				lowPassedConv = np.convolve(normalizedHpsPowers, gaussianPoints, 'same')
				currPatternSharpnessMeasure = np.sum(abs(lowPassedConv - normalizedHpsPowers)) / (len(currPatternPowers) - len(currPatternPowers) * gaussianPoints[1])
			else:
				currPatternSharpnessMeasure = 0 # only possible if minHarmonicsPerCandidate set to less then 2
			currPatternSmoothness = 1 - currPatternSharpnessMeasure
			combinationSalience += (totalPatternLoudness * currPatternSmoothness ** smoothnessImportance) ** 2

		return combinationSalience, harmonicsPatterns

	def post_process_midi_notes(resNotes):
		resultPianoRoll = []
		for i in range(0, len(resNotes)):
			pianoRollRow = np.zeros(maxMidiPitch)
			for notePitch, amplitude in resNotes[i].items():
				amplitude = min(np.round(amplitude * 6), 127)
				pianoRollRow[notePitch] = amplitude
			resultPianoRoll.append(pianoRollRow)

		return utilpost_process_midi_notes(resultPianoRoll, sampleRate, spacing, maxMidiPitch, minNoteMs, minNoteVelocity, 4)

	def coreMethod():
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
			allMidiNotes = []
			allResults = []
			allPatterns = []
			for combination in possibleCombinations:
				if newAlgorithmVersion:
					(combinationSalience, harmonicsPattern) = countCombinationSalience2(combination, patterns, peaks, ownerships) 
				else:
					combinationSalience = countCombinationSalience(combination, patterns, peaks, ownerships)
					harmonicsPattern = []
				allSaliences.append(combinationSalience)

				result = np.zeros(k1)
				midiNotes = {}
				for fftFq in combination:
					fq = fft_to_hz_array[fftFq]
					midiNotes[hz_to_midi(fq)] = (amplitudeSum[fftFq] / len(patterns[fftFq]))
					result[fftFq] = amplitudeSum[fftFq]
				allMidiNotes.append(midiNotes)
				allResults.append(result)
				allPatterns.append(harmonicsPattern)

			allCombinations.append(CombinationData(possibleCombinations, allSaliences, allMidiNotes, allResults, allPatterns))

			resF0Weights.append(allResults[np.argmax(allSaliences)])
			resNotes.append(allMidiNotes[np.argmax(allSaliences)])
		return resNotes, resF0Weights, peaks, allCombinations

	def flatternCombination(allCombinations):
		newSaliences = []
		for frame in range(0, len(allCombinations)):
			(currCombs, _, currMidiNotes, _, _) = allCombinations[frame]
			currNewSaliences = []
			for comb in range(0, len(currCombs)):
				newSalience = 0
				for k in range(-temporalSmoothnessRange, temporalSmoothnessRange + 1):
					(_, neighbourAllSaliences, neighbourMidiNotes, _, _) = allCombinations[min(max(frame + k, 0), len(allCombinations) - 1)]
					if currMidiNotes[comb] in neighbourMidiNotes:
						newSalience += neighbourAllSaliences[neighbourMidiNotes.index(currMidiNotes[comb])]
				currNewSaliences.append(newSalience)
			newSaliences.append(currNewSaliences)
		return newSaliences

	def pitchTracking(allCombinations, saliences):
		graph = nx.DiGraph()
		first_node = None
		last_node = None
		def countWeight(lvi, lvj, salience_j):
			D = 0
			fundamentals_i = map(lambda x: x[0], lvi)
			fundamentals_j = map(lambda x: x[0], lvj)
			for pattern_i in lvi:
				if pattern_i[0] in fundamentals_j:
					
					D += np.abs(sum(map(lambda a: a[1], pattern_i[1])) + sum(map(lambda a: a[1], [item for item in lvj if item[0] == pattern_i[0]][0][1])))
				else:
					D += sum(map(lambda a: a[1], pattern_i[1]))
			for pattern_j in lvj:
				if pattern_j[0] not in fundamentals_i:
					D += sum(map(lambda a: a[1], pattern_j[1]))
			return D / (salience_j + 1)

		for frame in range(0, len(allCombinations) - 1):
			(_, _, _, _, currPatterns) = allCombinations[frame]
			(_, _, _, _, nextPatterns) = allCombinations[frame + 1]

			currFrameSorted = get_arg_max(saliences[frame])
			nextFrameSorted = get_arg_max(saliences[frame + 1])
			for currVertex in range(0, min(len(currPatterns), pitch_tracking_combinations)):
				for nextFrameVertex in range(0, min(len(nextPatterns), pitch_tracking_combinations)):
					graph.add_edge((frame, currFrameSorted[currVertex]), (frame + 1, nextFrameSorted[nextFrameVertex]),\
						weight=countWeight(currPatterns[currFrameSorted[currVertex]], nextPatterns[nextFrameSorted[nextFrameVertex]], saliences[frame + 1][nextFrameSorted[nextFrameVertex]]))
					if first_node == None:
						first_node = (frame, currFrameSorted[currVertex])
					if frame + 1 == len(allCombinations) - 1:
						last_node = (frame, currFrameSorted[currVertex])
		
		path = nx.dijkstra_path(graph, first_node, last_node, weight='weight')

		resNotes = []
		for edge in path:
			resNotes.append(allCombinations[edge[0]][2][edge[1]])

		return path, graph, resNotes

	def pertusAndInesta2008():
		resNotes, resF0Weights, peaks, _ = coreMethod()

		resMidi, resPianoRoll = post_process_midi_notes(resNotes)

		return resMidi, resPianoRoll, resF0Weights, peaks, None, None

	def pertusAndInesta2012():
		resNotes, resF0Weights, peaks, allCombinations = coreMethod()
		newSaliences = flatternCombination(allCombinations)
		path, graph, resNotes = pitchTracking(allCombinations, newSaliences)
		resMidi, resPianoRoll = post_process_midi_notes(resNotes)

		return resMidi, resPianoRoll, resF0Weights, peaks, path, graph

	if newAlgorithmVersion:
		return pertusAndInesta2012()
	return pertusAndInesta2008()


def transcribe_by_joint_method_wrapped(filePath, newV, outPath):
	frameWidth = 8192
	spacing = 1024
	sampleRate, data = loadNormalizedSoundFIle(filePath)

	resMidi, resPianoRoll, resF0Weights, peaks, path, graph = harmonic_and_smoothness_based_transcription(
		data, sampleRate, frameWidth, spacing, frameWidth * 3, newAlgorithmVersion=newV)

	write_midi(resMidi, outPath)


if __name__ == "__main__":

	frameWidth = 8192
	spacing = 1024
	filePath = path.dirname(path.abspath(__file__))
	#filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
	#filePath = '../test_sounds/Sine_sequence.wav'
	#filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')
	filePath = path.join(filePath, '../test_sounds/Chopin_prelude28no.4inEm/chopin_prelude_28_4.wav')
	sampleRate, data = loadNormalizedSoundFIle(filePath)
	data = data[:(int(len(data)))]
	sampleRate = 44100

	sine_data = create_sine(220, sampleRate, 5)
	sine_data += (create_sine(440, sampleRate, 5) * 0.2)
	sine_data += (create_sine(110, sampleRate, 5) * 0.3)

	resMidi, resPianoRoll, resF0Weights, peaks, path, graph = harmonic_and_smoothness_based_transcription(
            data, sampleRate, frameWidth, spacing, frameWidth * 3, newAlgorithmVersion=True)

	write_midi(resMidi, "./res3.mid")
	plot_midi(resPianoRoll, spacing, sampleRate)
	plot_peaks(peaks, frameWidth, sampleRate)
	plot_spectrogram(resF0Weights, spacing, sampleRate)
	#plot_pitch_tracking(path, graph)
	print("ok")
