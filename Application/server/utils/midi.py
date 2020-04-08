from midiutil import MIDIFile
import numpy as np
import math
from io import BytesIO

def write_midi(note_grid, filename, spacing):
	midifile = MIDIFile(1)
	midifile.addTempo(0, 0, 60)
	for note in note_grid:
		midifile.addNote(0, 0, note.pitch, note.onsetMs, note.durotianMs, int(note.velocity))

	with open(filename, 'wb') as outfile:
		midifile.writeFile(outfile)

def get_midi_bytes(note_grid, spacing, duration=1):
	midifile = MIDIFile(1)
	midifile.addTempo(0, 0, 60)

	for note in note_grid:
		midifile.addNote(0, 0, note.pitch, note.onsetMs, note.durotianMs, int(note.velocity))
	
	res = BytesIO()

	midifile.writeFile(res)
	return res

def hz_to_midi(freq):
	return 69 + (int(np.round(12 * np.log2(freq / 440))))

def midi_to_hz(note):
	return math.pow(2, (note - 69) / 12) * 440

class MidiNote:
	def __init__(self, pitch, velocity, onsetMs, durotianMs):  
		self.pitch = pitch
		self.velocity = velocity
		self.onsetMs = onsetMs
		self.durotianMs = durotianMs

def res_in_hz_to_midi_notes(resInF0PerFrame, sampleRate, spacing):
	resultPianoRoll = []
	for fq in resInF0PerFrame:
		pianoRollRow = np.zeros(127)
		pianoRollRow[hz_to_midi(fq)] = 100
		resultPianoRoll.append(pianoRollRow)
	return postProcessMidiNotes(resultPianoRoll, sampleRate, spacing, 127, 40, 1)

def postProcessMidiNotes(pianoRoll, sampleRate, spacing, maxMidiPitch, minNoteMs, minNoteVelocity, neighbourMerging = 1):
	resultNotes = []
	noteTail = minNoteMs / 1000
	for note in range(0, maxMidiPitch):
		currDurotian = 0
		currVelocity = 0
		for i in range(0, len(pianoRoll)):
			leftExist = False
			rightExists = False
			for x in range(1, neighbourMerging + 1):
				if i - x > 0 and pianoRoll[i - 1][note] != 0:
					leftExist = True
				if len(pianoRoll) > i + x and pianoRoll[i + x][note] != 0:
					rightExists = True
			if pianoRoll[i][note] != 0 or (leftExist and rightExists):
				if pianoRoll[i][note] == 0:
					if currVelocity == 0:
						currVelocity = 80

					averageVelocity = currVelocity / max(currDurotian, 1)
					currVelocity += averageVelocity
					pianoRoll[i][note] = averageVelocity
				else:
					currVelocity += pianoRoll[i][note]
				currDurotian += 1
			elif (currDurotian * spacing / sampleRate) * 1000 > minNoteMs:
				onsetIdx = i - currDurotian
				currVelocity /= currDurotian
				currDurotianMs = currDurotian * spacing / sampleRate + noteTail
				if currVelocity > minNoteVelocity:
					resultNotes.append(
						MidiNote(note, currVelocity, onsetIdx * spacing / sampleRate, currDurotianMs))
				currDurotian = 0
				currVelocity = 0
			else:
				currDurotian = 0
				currVelocity = 0
	return resultNotes, pianoRoll
