from midiutil import MIDIFile
import numpy as np
import math 
def write_midi(note_grid, filename, spacing, duration=1):
	midifile = MIDIFile(1)
	midifile.addTempo(0, 0, 60)
	# for i, notes in enumerate(note_grid):
	# 	time = i*spacing
	# 	for k, level in enumerate(notes):
	# 		if level > 0.1 and (i == 0 or prev_notes[k] < 0.1):
	# 			print(i, k, level)
	# 			midifile.addNote(0, 0, k - 1, float(time), duration, int(level))
	# 	prev_notes = notes
	for note in note_grid:
		midifile.addNote(0, 0, note.pitch, note.onsetMs, note.durotianMs, int(note.velocity))

	with open(filename, 'wb') as outfile:
		midifile.writeFile(outfile)

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
