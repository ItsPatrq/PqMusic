from midiutil import MIDIFile
import numpy as np
import math
from io import BytesIO

def write_midi(note_grid, filename, spacing, duration=1):
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
