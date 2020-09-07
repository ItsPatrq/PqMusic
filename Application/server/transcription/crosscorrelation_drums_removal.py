"""
W tym module znajduje się metoda usuwająca elementy perkusyjne z sygnału wejściowego.
Algorytm nie jest opisany w pracy pisemnej. Autorska metoda miała wykrywać początki dźwięków
i porównywać je z bazą przykładowych dźwięków perkusyjnych przy pomocy kross-korelacji.
W przypadku dopasowania dźwięk zostawał usuwany z widma.
Problem pojawia się przy nawet najmniejszym błędzie wykrycia faktycznego początku nuty
odjęcie takiego dźwięku z widma z drobnym przesunięciem od faktycznego dźwięku w wyniku
powoduje występowanie dwóch takich dźwięków pod rząd, z tym że jeden ma odwróconą fazę.
"""

import sys
from os import path
from aubio import onset, source  # pylint: disable=no-name-in-module
import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft, ifft
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.general import loadNormalizedSoundFile, to_wave # pylint: disable=import-error

# do wykrywania początków dźwięków używana jest biblioteka aubio

def detect_onsets(file_path, window_size=1024):
    """
    Zwraca listę indeksów wykrytych początków dźwięków.
    Args:
        file_path: ścieżka do sprawdzanego pliku,
        window_size: wielkość okna
    """

    hop_s = window_size // 2
    get_data = source(file_path, hop_size=hop_s)
    sample_rate = get_data.samplerate

    get_onset = onset("default", window_size, hop_s, sample_rate)

    # lista początków dźwięków
    onsets = []

    # liczba wczytanych okien
    total_frames = 0
    while True:
        samples, read = get_data()
        if get_onset(samples):
            onsets.append(get_onset.get_last())
        total_frames += read
        if read < hop_s:
            break
    return onsets


def spectral_removal(input_data, sound_to_be_removed, occurrences,
                     frame_width=4096, size_of_zero_padding=4096):
    """
    Usuwa dźwięk $sound_to_be_removed w domenie fq z sygnału $input_data
    dla każdego indeksu occurrences.
    """
    copied_data = np.array(input_data)
    zeropad = np.zeros(size_of_zero_padding)

    def remove_sound1_from_sound2(sound1, sound2):
        fft_1 = fft(np.concatenate((sound1, zeropad)))
        fft_2 = fft(np.concatenate((sound2, zeropad)))
        fft_1 -= fft_2.real
        return ifft(fft_1).real[:len(sound1)]

    for occurrence in occurrences:
        for i in range(0, int(math.ceil((len(sound_to_be_removed) - frame_width) / frame_width))):
            if len(copied_data) < occurrence+i*frame_width:
                break
            max_data_len = min(len(sound_to_be_removed) - i*frame_width,
                               frame_width, len(copied_data) - (occurrence+i*frame_width))
            base_sound_window = copied_data[(
                occurrence+i*frame_width):(occurrence+i*frame_width+max_data_len)]
            removed_sound_window = sound_to_be_removed[(
                i*frame_width):(i*frame_width+max_data_len)]
            removed = remove_sound1_from_sound2(base_sound_window, removed_sound_window)
            copied_data[(occurrence+i*frame_width):(occurrence +
                                                    i*frame_width+max_data_len)] = removed

    return copied_data


def cross_correlation(input_data, onsets, example_sounds, frame_width=4096,
                      size_of_zero_padding=4096, spacing=4096, onset_missplace=10):
    """
    Wyliczenie kross-korelacji
    """
    zeropad = np.zeros(size_of_zero_padding)

    def corr(ang_a, ang_b):
        # cosinus konta pomiędzy kontem ang_a i ang_b
        div = np.linalg.norm(ang_a) * np.linalg.norm(ang_b)
        fft_a = fft(np.concatenate((ang_a, zeropad)))
        fft_rev_b = fft(list(reversed(np.concatenate((ang_b, zeropad)))))
        crossCorrelation = abs(ifft(fft_a * fft_rev_b))
        return crossCorrelation / div

    possible_events = {}
    for curr_onset in tqdm(onsets):
        curr_sounds_correlations = []
        for sound_index, sound in enumerate(example_sounds):
            curr_correlations = []
            for shifted_onset in range(max(curr_onset-onset_missplace, 0),
                                      min(curr_onset+onset_missplace, len(input_data))):
                for i in range(0, int(math.ceil((len(sound) - frame_width) / spacing))):
                    if len(input_data) < shifted_onset+i*spacing:
                        break
                    max_data_len = min(len(sound) - i*spacing, frame_width,
                                       len(input_data) - (shifted_onset+i*spacing))
                    base_sound_window = input_data[(
                        shifted_onset+i*spacing):(shifted_onset+i*spacing+max_data_len)]
                    testedSoundWindow = sound[(
                        i*spacing):(i*spacing+max_data_len)]
                    correlation = corr(base_sound_window, testedSoundWindow)
                    curr_correlations.append(max(correlation))
                avg = sum(curr_correlations) / len(curr_correlations)
                curr_sounds_correlations.append((avg, sound_index))
        max_element = np.argmax(np.array( # pylint: disable=unsubscriptable-object
            curr_sounds_correlations).T[0])
        if round(curr_sounds_correlations[max_element][0], 1) >= 0.3:
            possible_events[curr_onset] = curr_sounds_correlations[max_element][1]
    return possible_events


def drums_removal_example():
    """
    Przykład użycia metody usuwania perkusji przy pomocy kross-korelacji
    """
    frame_width = 2048
    spacing = 512
    file_path = path.dirname(path.abspath(__file__))
    track_path = path.join(file_path, '../test_sounds/example/track.wav')
    sample_rate, data = loadNormalizedSoundFile(track_path)
    sounds = []
    paths = [
        path.join(file_path, '../test_sounds/example/track_kick.wav'),
        path.join(file_path, '../test_sounds/example/track_snare.wav'),
        path.join(file_path, '../test_sounds/example/track_hihat1.wav'),
        path.join(file_path, '../test_sounds/example/track_hiHat2.wav'),
    ]

    for currPath in paths:
        _, sound_data = loadNormalizedSoundFile(currPath)
        sounds.append(sound_data)
    sample_rate = 44100
    onsets = detect_onsets(track_path)
    res1 = cross_correlation(data, onsets, sounds,
                             frame_width, frame_width, spacing)
    occurrences = []
    while len(occurrences) < len(sounds):
        occurrences.append([])
    for key, value in res1.items():
        occurrences[value].append(key)

    for i in range(0, len(sounds)):
        res = spectral_removal(data, sounds[i], occurrences[i])
    to_wave(res, sample_rate, "crossCorrelationDrumsRemoval.wav")


if __name__ == "__main__":
    drums_removal_example()
