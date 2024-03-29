"""
W tym module znajdują się metody pomocnicze do obsługi standardu MIDI (zapis/odczyt) wraz z metodą porównującą dwie rolki pianina
"""

from midiutil import MIDIFile
import numpy as np
import math
from mido import MidiFile, tick2second


def write_midi(note_grid, filename):
    midifile = MIDIFile(1)
    midifile.addTempo(0, 0, 60)
    for note in note_grid:
        midifile.addNote(0, 0, note.pitch, note.onsetS,
                         note.durationS, int(note.velocity))

    with open(filename, 'wb') as outfile:
        midifile.writeFile(outfile)


def hz_to_midi(freq):
    """
    funkcja wyznaczająca indeks tonacji na podstawie hz
    """
    return 69 + (int(np.round(12 * np.log2(freq / 440))))


def midi_to_hz(note):
    return math.pow(2, (note - 69) / 12) * 440


class MidiNote:
    """
    Klasa pomocnicza do zdefiniowania struktury MIDI w projekcie
    """

    def __init__(self, pitch, velocity, onsetS, durationS):
        self.pitch = pitch
        self.velocity = velocity
        self.onsetS = onsetS
        self.durationS = durationS

    def print_self(self):
        print(self.pitch, self.velocity, self.onsetS, self.durationS)


def res_in_hz_to_midi_notes(res_in_f0_per_frame, sample_rate, spacing, neighbour_merging=1):
    """
    Funkcja tranformująca wynik detekcji F0 do postaci rolki pianina dla sygnału monofonicznego. 
    Wartość dynamiki ustawiana jest zawsze na 100
    """
    result_piano_roll = []
    for fq in res_in_f0_per_frame:
        piano_roll_row = np.zeros(127)
        if fq > 0:
            piano_roll_row[hz_to_midi(fq)] = 100
        result_piano_roll.append(piano_roll_row)
    return post_process_midi_notes(result_piano_roll, sample_rate, spacing, 127, 1, 0, neighbour_merging)


def post_process_midi_notes(pianoRoll, sampleRate, spacing, maxMidiPitch, minNoteMs, minNoteVelocity, neighbourMerging=1):
    """
    przetwarzanie końcowe MIDI. Wycinane są takie zdarzenia, których głośność i/lub długość nie przekracza
    zadanego argumentami $minNoteMs/$minNoteVelocity progu.
    W tej funkcji następije scalanie 'luk' w nutach w zasięgu +-$neighbourMerging
    (gdy ton w oknie idx-1 oraz oknie idx+1 jest wykryty,a w idx nie, to gdy neighbourMerging >= 1
    zakłada się, że  w idx też jest wykryty.)
    """
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
    """
    Wczytywanie pliku MIDI w postaci eventów zgodnych ze strukturą
    projektu, czyli w postaci instancji klas MidiNote
    """
    note_on = "note_on"
    note_off = "note_off"
    set_tempo = "set_tempo"
    mid = MidiFile(filePath, clip=True)

    def get_midi_notes(midiTrack, microPerBeat):
        resultNotes = []
        for note in range(0, 127):
            start_tick = 0
            curr_ticks = 0
            last_event = None
            last_vel = 0
            for midiNoteEvent in midiTrack:  # note_on zawsze będą przed note_off danej nuty
                if midiNoteEvent.type in [note_on, note_off]:
                    curr_ticks += midiNoteEvent.time
                    if note == midiNoteEvent.note and last_event != note_on:
                        start_tick = curr_ticks
                        last_event = note_on
                        last_vel = midiNoteEvent.velocity
                    # onsets and frames nie zwraca zdarzeń typu note_ff tylko note_on z velocity = 0 jako koniec nuty
                    elif note == midiNoteEvent.note and (midiNoteEvent.velocity == 0 or midiNoteEvent.type == note_off):
                        resultNotes.append(
                            MidiNote(note, last_vel, tick2second(start_tick, mid.ticks_per_beat, microPerBeat), tick2second(curr_ticks - start_tick, mid.ticks_per_beat, microPerBeat)))
                        last_event = note_off

        return resultNotes

    def get_tempo_info(midiTrack):
        for meta in midiTrack:
            if meta.is_meta and meta.type == set_tempo:
                return meta.tempo
        raise Exception("Given MIDI has no tempo information")

    if mid.type == 2:
        raise NotImplementedError(
            "Only type 0 and 1 MIDI files can be loaded (single-track / multiple tracks, synchronous). Got " + str(mid.type))
    if len(mid.tracks) > 2:
        print("Only notes from 1st track will be loaded")
    if len(mid.tracks) < 1:
        raise OSError(
            "There should be at least one tracks in MIDI, found less")

    return get_midi_notes(mid.tracks[0] if mid.type == 0 else mid.tracks[1], get_tempo_info(mid.tracks[0]))


def compare_midi_to_ground_truth(transcriptionMidiNotes, groundTruthMidiNotes, maxError=0.003):
    """
    Porównanie wynik transkrypcji z pliku $transcriptionMidiNotes do pliku
    z danymi faktycznymi $groundTruthMidiNotes z maksymalnym błędem czasu
    wynoszącym $maxError
    """
    FN = 0  # false negative
    FP = 0  # false positive
    TP = 0  # true positive

    def areNotesAlike(noteChecked, noteGt):
        onsetChecked, durChecked = noteChecked.onsetS, noteChecked.durationS
        onsetGt, durGt = noteGt.onsetS, noteGt.durationS
        if onsetChecked <= onsetGt + maxError and onsetChecked >= onsetGt - maxError and \
                durChecked <= durGt + maxError and durChecked >= durGt - maxError:
            return True
        return False

    # w tej petli sprawdzane tylko FP
    for i in range(0, len(transcriptionMidiNotes)):
        found = False
        for j in range(0, len(groundTruthMidiNotes)):
            if areNotesAlike(transcriptionMidiNotes[i], groundTruthMidiNotes[j]):
                found = True
                break
        if not found:
            FP += 1

    for i in range(0, len(groundTruthMidiNotes)):
        found = False
        for j in range(0, len(transcriptionMidiNotes)):
            if areNotesAlike(transcriptionMidiNotes[j], groundTruthMidiNotes[i]):
                found = True
                break
        if found:
            TP += 1
        else:
            FN += 1
    if TP + FP == 0:
        percision = 0
    else:
        percision = TP / (TP + FP)

    accuracy = TP / (TP + FP + FN)
    recall = TP / (TP + FN)
    if percision == 0 and recall == 0:
        F1 = 0
    else:
        F1 = 2 * (percision * recall / (percision + recall))

    return FN, FP, TP, F1, percision, recall, accuracy


if __name__ == "__main__":
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    filePathAbs = path.dirname(path.abspath(__file__))
