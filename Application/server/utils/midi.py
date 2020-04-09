from midiutil import MIDIFile
import numpy as np
import math
from io import BytesIO
from mido import MidiFile, tick2second

def write_midi(note_grid, filename):
	midifile = MIDIFile(1)
	midifile.addTempo(0, 0, 60)
	for note in note_grid:
		midifile.addNote(0, 0, note.pitch, note.onsetS, note.durationS, int(note.velocity))

	with open(filename, 'wb') as outfile:
		midifile.writeFile(outfile)

def get_midi_bytes(note_grid, spacing, duration=1):
	midifile = MIDIFile(1)
	midifile.addTempo(0, 0, 60)

	for note in note_grid:
		midifile.addNote(0, 0, note.pitch, note.onsetS, note.durationS, int(note.velocity))
	
	res = BytesIO()

	midifile.writeFile(res)
	return res

def hz_to_midi(freq):
	return 69 + (int(np.round(12 * np.log2(freq / 440))))

def midi_to_hz(note):
	return math.pow(2, (note - 69) / 12) * 440

class MidiNote:
	def __init__(self, pitch, velocity, onsetS, durationS):  
		self.pitch = pitch
		self.velocity = velocity
		self.onsetS = onsetS
		self.durationS = durationS

	def print_self(self):
		print(self.pitch, self.velocity, self.onsetS, self.durationS)

def res_in_hz_to_midi_notes(resInF0PerFrame, sampleRate, spacing):
	resultPianoRoll = []
	for fq in resInF0PerFrame:
		pianoRollRow = np.zeros(127)
		pianoRollRow[hz_to_midi(fq)] = 100
		resultPianoRoll.append(pianoRollRow)
	return post_process_midi_notes(resultPianoRoll, sampleRate, spacing, 127, 1, 0, 0)

def post_process_midi_notes(pianoRoll, sampleRate, spacing, maxMidiPitch, minNoteMs, minNoteVelocity, neighbourMerging = 1):
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
				currdurationS = currDurotian * spacing / sampleRate + noteTail
				if currVelocity > minNoteVelocity:
					resultNotes.append(
						MidiNote(note, int(currVelocity), onsetIdx * spacing / sampleRate, currdurationS))
				currDurotian = 0
				currVelocity = 0
			else:
				currDurotian = 0
				currVelocity = 0
	return resultNotes, pianoRoll

def load_midi_file(filePath):
	note_on = "note_on"
	note_off = "note_off"
	set_tempo = "set_tempo"
	mid = MidiFile(filePath, clip=True)

	if mid.type != 1:
		raise NotImplementedError("Only type 1 MIDI files can be loaded (synchronous)")
	if len(mid.tracks) > 2:
		print("Only notes from first channel will be loaded")
	if len(mid.tracks) < 2:
		raise OSError("There should be two tracks in MIDI, found less")
	bpm = 0
	for meta in mid.tracks[0]:
		if meta.is_meta and meta.type == set_tempo:
			microPerBeat = meta.tempo 
			bpm = 60 / (meta.tempo * 0.000001) ## meta.tempo jest w microsekundach, czyli 0.000001 części sekundy
	resultNotes = []
	for note in range(0, 127):
		start_tick = 0
		curr_ticks = 0
		for midiNoteEvent in mid.tracks[1]: ## note_on zawsze będą przed note_off danej nuty
			if midiNoteEvent.type in [note_on, note_off]:
				curr_ticks += midiNoteEvent.time
				if note == midiNoteEvent.note and midiNoteEvent.type == note_on:
					start_tick = curr_ticks
				elif  note == midiNoteEvent.note and midiNoteEvent.type == note_off:
					resultNotes.append(
						MidiNote(note, midiNoteEvent.velocity, tick2second(start_tick, mid.ticks_per_beat, microPerBeat), tick2second(curr_ticks - start_tick, mid.ticks_per_beat, microPerBeat)))
	return resultNotes

def compare_midi_to_ground_truth(transcriptionMidiNotes, groundTruthMidiNotes):
	fp = 0
	fn = 0
	tp = 0
	transcription_checked = []
	ground_checked = []
	for i in range(0, len(transcriptionMidiNotes)):
		currOnset, currrDurr = transcriptionMidiNotes[i].onsetS, transcriptionMidiNotes[i].durationS
		for i in range(0, len(groundTruthMidiNotes)):
			print("TODO")
	
if __name__ == "__main__":
	from os import path
	import sys
	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
	filePath = path.dirname(path.abspath(__file__))
	#filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')
	#filePath = '../test_sounds/Sine_sequence.wav'
	#filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')
	filePath = path.join(filePath, '../resAC.mid')
	res = load_midi_file(filePath)
	print(res)
	write_midi(res, './x.mid')
