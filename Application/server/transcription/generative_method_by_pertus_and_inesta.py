"""
W tym module znajdują się implementacje metod Pertusa i Iñesta z 2008 i 2012 roku.
"""

from collections import namedtuple
import networkx as nx
import math
import numpy as np
from tqdm import tqdm
from scipy.fftpack import fft
from copy import deepcopy
from itertools import combinations

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.cepstrum_utils import lifter_on_power_spec, LifterType  # pylint: disable=import-error
from utils.plots import plot_spectrogram, plot_midi, plot_peaks  # pylint: disable=import-error
from utils.general import loadNormalizedSoundFile, fft_to_hz, hz_to_fft, get_arg_max  # pylint: disable=import-error
from utils.midi import write_midi, hz_to_midi, midi_to_hz, post_process_midi_notes as utilpost_process_midi_notes  # pylint: disable=import-error

def harmonic_and_smoothness_based_transcription(data, sample_rate, neighbour_merging=4, frame_width=8192, spacing=1024, size_of_zero_padding=24576,
                                                min_f0=85, max_f0=5500, peak_distance=8, relevant_power_threashold=4, max_inharmony_degree=0.08, min_harmonics_per_candidate=2,
                                                max_harmonics_per_candidate=10, max_candidates=8, max_parallel_notes=5, gamma=0.05, min_note_ms=70,
                                                liftering_coefficient=8, min_note_velocity=10, new_algorithm_version=True,
                                                smoothness_importance=3, temporal__smoothness_range=2, pitch_tracking_combinations=3, disable_tqdm=True):
    """
    Funkcja do transkrypcji sygnału metodą Pertusa i Iñesta z 2008 lub 2012 roku.
    W zależności od parametru new_algorithm_version wykonywana jest metoda
    pertus_and_inesta_2008 (False) lub pertus_and_inesta_2012 (True)
    Params:
        neighbour_merging: ilość analizowanych sąsiednich nut przy scalaniu podczas przetwarzania końcowego,
        frame_width: długość okna w samplach,
        spacing: odstępy pomiędzy kolejnymi oknami,
        size_of_zero_padding: wymiar tablicy zer dodanej do okna przed wykonaniem FFT,
        min_f0:  minimalna częstotliwość, jaka jest analizowana w kontekście F0 (w Hz),
        max_f0:  maksymalna częstotliwość, jaka jest analizowana w kontekście F0 (w Hz),
        peak_distance: minimalny odstęp pomiędzy pikami w amplitudzie (w samplach),
        relevant_power_threashold: próg amplitudy, poniżej którego zerowane są wartości,
        min_harmonics_per_candidate: minimalna ilość harmonicznych dla kandydata F0,
        gamma: maksymalna różnica w parametrze głośności w kombinacji,
        max_inharmony_degree: maksymalna nieharmoniczność,
        max_parallel_notes: maksymalna ilość równoległych dźwięków,
        liftering_coefficient: mnożnik lifteringu. Dla wartości 0 funkcja lifteringu nie jest wykonywana,
        smoothness_importance: ważność współczynnika gładkości,
        temporal__smoothness_range: zakres wygładzania czasowego (w oknach czasowych),
        pitch_tracking_combinations: zakres śledzenia wysokości (w oknach czasowych),
        new_algorithm_version: False - wersja z 2008, True - wersja z 2012
    """

    #region init values
    hann = np.hanning(frame_width)
    resF0Weights = []
    resNotes = []
    zeropad = np.zeros(size_of_zero_padding)
    gaussian_points = [0.21, 0.58, 0.21]
    fftLen = int(np.floor((frame_width + size_of_zero_padding)/2))

    fft_to_hz_array = fft_to_hz(sample_rate, fftLen)
    hz_to_fft_array = hz_to_fft(sample_rate, frame_width*2)

    k0 = int(np.round(hz_to_fft_array[min_f0]))
    k1 = int(np.round(hz_to_fft_array[max_f0]))

    max_midi_pitch = 127
    CombinationData = namedtuple(
        'CombinationData', "possible_combinations all_saliences all_midi_notes all_results all_patterns")
    #endregion init values

    def countMaxInharmonyFrequencies(expectedFft):
        """
        Zwracana najniższa i najwyższa możliwa częstotliwość dla danej
        częstotliwości expectedFft jakie może przyjmować harmoniczna dla
        danego parametru nieharmoniczności max_inharmony_degree
        """
        expectedFq = fft_to_hz_array[expectedFft]
        currNote = hz_to_midi(expectedFq)
        currNoteFq = midi_to_hz(currNote)
        prevNoteFq = midi_to_hz(currNote - 1)
        nextNoteFq = midi_to_hz(currNote + 1)
        return int(np.round((currNoteFq - prevNoteFq) * max_inharmony_degree)), int(np.round((nextNoteFq - currNoteFq) * max_inharmony_degree))

    def getCandidatesThatHaveEnoughHarmonics(candidate, peaks):
        """
        Dla danych kandydatów i im odpowiadającym pikom, sprawdza ilość
        harmonicznych kandydatów z braniem pod uwagę nieharmoniczności
        Res:
            hypotheses: lista hipotez F0 mających > min_harmonics_per_candidate harmonicznych
            amplitude_sum: tablica sum aplitud harmonicznych kandydatów
            patterns: tablica wzorów spektralnych kandydatów
            ownerships: słownik zawierający informacje, jacy kandydaci posiadają jakie harmoniczne
        """
        hypotheses = []
        amplitude_sum = np.zeros(k1)
        patterns = {}
        ownerships = {}
        for f0_candidate in candidate:
            harmonics_found = 0
            curr_amplitude_sum = np.array(amplitude_sum)
            curr_patterns = deepcopy(patterns)
            curr_ownerships = deepcopy(ownerships)
            curr_amplitude_sum[f0_candidate] = peaks[f0_candidate]
            curr_patterns[f0_candidate] = [(f0_candidate, peaks[f0_candidate])]
            for harmonic in range(2, max_harmonics_per_candidate):
                currExpHarFft = harmonic * f0_candidate
                if currExpHarFft > len(peaks) - 1:
                    break
                max_left_inh, max_right_inh = countMaxInharmonyFrequencies(
                    currExpHarFft)
                max_curr_harmonic = min(
                    len(peaks) - 1, int(currExpHarFft + max_right_inh))
                range_of_best_fq = peaks[(
                    currExpHarFft - max_left_inh):max_curr_harmonic]
                if len(range_of_best_fq) == 0:
                    break
                best_fq = np.argmax(range_of_best_fq) + currExpHarFft - max_left_inh
                bestPow = peaks[best_fq]
                if bestPow > 0:
                    harmonics_found += 1
                    if best_fq in curr_ownerships:
                        curr_ownerships[best_fq].append(f0_candidate)
                    else:
                        curr_ownerships[best_fq] = [f0_candidate]
                    curr_amplitude_sum[f0_candidate] += bestPow
                    curr_patterns[f0_candidate].append((best_fq, bestPow))
            if harmonics_found >= min_harmonics_per_candidate:
                hypotheses.append(f0_candidate)
                amplitude_sum = curr_amplitude_sum
                patterns = curr_patterns
                ownerships = curr_ownerships
        return hypotheses, amplitude_sum, patterns, ownerships

    def updateMinMaxL(loudness, highest_loudness, lowest_loudness):
        """
        Funkcja pomocnicza do porównania głośności
        Res:
            highest_loudness: największa wartość głośności
            lowest_loudness: najmniejsza wartość głośności
        """
        if highest_loudness is None or highest_loudness < loudness:
            highest_loudness = loudness
        if lowest_loudness is None or lowest_loudness > loudness:
            lowest_loudness = loudness
        return highest_loudness, lowest_loudness

    def count_power_fft_window(i):
        """
        Res:
            powerSp: wyliczone spektrum mocy dla okna czasowego o indeksie i, W przypadku
                gdy parametr liftering_coefficient ma wartość dodatnią, zwracane jest spektrum
                mocy po filtrowaniu w domenie cepstrum
        """
        frame = data[i*spacing:i*spacing+frame_width] * hann
        frame = np.concatenate((frame, zeropad))
        frame_complex = fft(frame)
        power_sp_window = abs(frame_complex)
        if liftering_coefficient is not None and liftering_coefficient > 0:
            return lifter_on_power_spec(power_sp_window, LifterType.sine, liftering_coefficient)[:fftLen]
        else:
            return power_sp_window[:fftLen]

    def get_peaks_and_candidates(power_sp_window):
        """
        Res:
            peaks: tablica długości wejściowego spektra mocy, z jedynie wartościami będącymi pikami
            candidate: lista kandydatów F0
        """
        peaks = np.zeros(len(power_sp_window))
        candidate = []

        for k in range(1, len(power_sp_window)-1):
            currPower = power_sp_window[k]
            if currPower > relevant_power_threashold and np.argmax(power_sp_window[max(k-peak_distance, 0):k+peak_distance+1]) + k-peak_distance == k:
                peaks[k] = currPower
                if k > k0 and k < k1:
                    candidate.append(k)

        return peaks, candidate

    def getmax_candidatesByPower(amplitude_sum, hypotheses):
        """
        Zwracane max_candidates kandydatów o największej sumie amplitud harmonicznych
        """
        sorted_by_pow = []
        cp_amplitude_sum = np.array(amplitude_sum)
        for _ in list(amplitude_sum.nonzero()[0]):
            maxFq = np.argmax(cp_amplitude_sum)
            if maxFq == 0:
                break
            cp_amplitude_sum[maxFq] = 0
            if maxFq in hypotheses:
                sorted_by_pow.append(maxFq)

        sorted_by_pow = sorted_by_pow[:max_candidates]
        return np.sort(sorted_by_pow)

    def smoothen_pattern(curr_pattern, curr_peaks, ownerships):
        """
        Funkcja implementująca wzorzec gładkości spektrum.
        Args:
            curr_pattern: wzorce spektralne
            curr_peaks: piki amplitudy
            ownerships: słownik właścicieli harmonicznych
        Res:
            curr_pattern: wzorzec po nałożeniu gładkości spektrum
            curr_peaks: piki po nałożeniu gładkości spektrum
        """
        pattern_harmonics_to_delete = []

        for harmonic in range(1, len(curr_pattern)):
            curr_harmonic_fft = curr_pattern[harmonic][0]
            # it was taken by other harmonic due to shared pattern
            if curr_peaks[curr_harmonic_fft] == 0:
                pattern_harmonics_to_delete.append(harmonic)
            elif len(ownerships[curr_harmonic_fft]) > 1:  # shared harmonic
                if len(curr_pattern) == harmonic + 1:
                    if len(curr_pattern) > 2:
                        interpolated_pitch = max(curr_pattern[harmonic - 1][1] - (
                            (curr_pattern[harmonic - 2][1] - curr_pattern[harmonic - 1][1]) / 2), 0)
                    else:
                        interpolated_pitch = curr_peaks[curr_pattern[harmonic][0]]
                else:
                    interpolated_pitch = (
                        curr_pattern[harmonic - 1][1] + curr_peaks[curr_pattern[harmonic + 1][0]]) / 2
                if interpolated_pitch > curr_peaks[curr_harmonic_fft]:
                    curr_pattern[harmonic] = (
                        curr_harmonic_fft, curr_peaks[curr_harmonic_fft])
                    curr_peaks[curr_harmonic_fft] = 0
                else:
                    curr_pattern[harmonic] = (
                        curr_harmonic_fft, interpolated_pitch)
                    curr_peaks[curr_harmonic_fft] = max(
                        curr_peaks[curr_harmonic_fft] - interpolated_pitch, 0)
            else:  # non-shared harmonic
                curr_pattern[harmonic] = (
                    curr_harmonic_fft, curr_peaks[curr_harmonic_fft])
                curr_peaks[curr_harmonic_fft] = 0
        for i in range(-1, -(len(pattern_harmonics_to_delete) + 1), -1):
            del curr_pattern[pattern_harmonics_to_delete[i]]
        return curr_pattern, curr_peaks

    def countcombination_salience(combination, patterns, peaks, ownerships):
        """
        Funkcja licząca istotność kombinacji dla metody z 2008 roku
        """
        curr_patterns = deepcopy(patterns)
        curr_peaks = np.array(peaks)
        combination_salience = 0
        highest_loudness = None
        lowest_loudness = None
        for fundamental in combination:
            curr_pattern, curr_peaks = smoothen_pattern(
                curr_patterns[fundamental], curr_peaks, ownerships)

            curr_pattern_powers = np.array(curr_pattern)
            curr_pattern_powers = curr_pattern_powers.T[1]  # pylint: disable=unsubscriptable-object
            total_pattern_loudness = np.sum(curr_pattern_powers)
            highest_loudness, lowest_loudness = updateMinMaxL(
                total_pattern_loudness, highest_loudness, lowest_loudness)
            if len(curr_pattern_powers) > 2:
                low_passed_conv = np.convolve(
                    curr_pattern_powers, gaussian_points, 'same')
                curr_pattern_sharpness_measure = np.sum(
                    abs(low_passed_conv - curr_pattern_powers)) / len(curr_pattern_powers)
            else:
                # możliwe tylko, jeśli min_harmonics_per_candidate jest ustawiony na mniej niż 2
                curr_pattern_sharpness_measure = 0
            curr_pattern_smoothness = 1 - curr_pattern_sharpness_measure
            combination_salience += (total_pattern_loudness *
                                     curr_pattern_smoothness) ** 2
        if lowest_loudness < highest_loudness * gamma:
            combination_salience = 0.0
        return combination_salience

    def countcombination_salience2(combination, patterns, peaks, ownerships):
        """
        Funkcja licząca istotność kombinacji dla metody z 2012 roku
        """
        curr_patterns = deepcopy(patterns)
        curr_peaks = np.array(peaks)
        combination_salience = 0
        highest_loudness = None
        lowest_loudness = None
        harmonics_patterns = []
        for fundamental in combination:
            curr_pattern, curr_peaks = smoothen_pattern(
                curr_patterns[fundamental], curr_peaks, ownerships)
            harmonics_patterns.append(
                (hz_to_midi(fft_to_hz_array[fundamental]), curr_pattern))

            curr_pattern_powers = np.array(curr_pattern)
            curr_pattern_powers = curr_pattern_powers.T[1]  # pylint: disable=unsubscriptable-object
            total_pattern_loudness = np.sum(curr_pattern_powers)
            highest_loudness, lowest_loudness = updateMinMaxL(
                total_pattern_loudness, highest_loudness, lowest_loudness)
            if lowest_loudness < highest_loudness * gamma:
                return 0.0, harmonics_patterns

            normalized_hps_powers = np.array(
                curr_pattern_powers) / np.max(curr_pattern_powers)
            if len(curr_pattern_powers) > 2:
                low_passed_conv = np.convolve(
                    normalized_hps_powers, gaussian_points, 'same')
                curr_pattern_sharpness_measure = np.sum(abs(low_passed_conv - normalized_hps_powers)) / (
                    len(curr_pattern_powers) - len(curr_pattern_powers) * gaussian_points[1])
            else:
                # możliwe tylko, jeśli min_harmonics_per_candidate jest ustawiony na mniej niż 2
                curr_pattern_sharpness_measure = 0
            curr_pattern_smoothness = 1 - curr_pattern_sharpness_measure
            combination_salience += (total_pattern_loudness *
                                     curr_pattern_smoothness ** smoothness_importance) ** 2

        return combination_salience, harmonics_patterns

    def post_process_midi_notes(resNotes):
        result_piano_roll = []
        for i in range(0, len(resNotes)):
            piano_roll_row = np.zeros(max_midi_pitch)
            for note_pitch, amplitude in resNotes[i].items():
                amplitude = min(np.round(amplitude * 6), 127)
                piano_roll_row[note_pitch] = amplitude
            result_piano_roll.append(piano_roll_row)

        return utilpost_process_midi_notes(result_piano_roll, sample_rate, spacing, max_midi_pitch, min_note_ms, min_note_velocity, neighbour_merging)

    def core_method():
        """
        Część wspólna obu metod (z 2008 i 2012), wykonywana jako pierwszy krok algorytmu.
        Dla każdego okna danych wejściowych wyznaczani są kandydaci hipotezy F0,
        które są następnie sortowane i sprawdzane pod względem ilości harmonicznych.
        Z kandydatów generowane są kombinacje, dla których są liczone istotności w sposób
        zależny od wersji metody, i przechowywane w tablicy all_saliences.
        Dla każdej kombinacji generowana jest rolka pianina i przechowywana w tablicy all_results,
        oraz lista zdarzeń MIDI przechowywana w all_midi_notes. Wszystkie kombinacje są zwracane
        w postaci list all_combinations, która zawiera dla każdej kombinacji wyliczoną istotność,
        zdarzenia MIDI, rolkę pianina oraz wzorzec spektralny. Te informacje potrzebne są w
        przetwarzaniu końcowym.
        """

        all_combinations = []
        for i in tqdm(range(0, int(math.ceil((len(data) - frame_width) / spacing))), disable=disable_tqdm):
            peaks, candidate = get_peaks_and_candidates(count_power_fft_window(i))

            hypotheses, amplitude_sum, patterns, ownerships = getCandidatesThatHaveEnoughHarmonics(
                candidate, peaks)
            if len(hypotheses) == 0:
                resNotes.append({})
                continue

            sorted_by_fq = getmax_candidatesByPower(amplitude_sum, hypotheses)

            possible_combinations = []
            for num_pitches in range(1, min(max_parallel_notes, len(sorted_by_fq)) + 1):
                for combo in combinations(sorted_by_fq, num_pitches):
                    possible_combinations.append(combo)

            all_saliences = []
            all_midi_notes = []
            all_results = []
            all_patterns = []
            for combination in possible_combinations:
                if new_algorithm_version:
                    (combination_salience, harmonicsPattern) = countcombination_salience2(
                        combination, patterns, peaks, ownerships)
                else:
                    combination_salience = countcombination_salience(
                        combination, patterns, peaks, ownerships)
                    harmonicsPattern = []
                all_saliences.append(combination_salience)

                result = np.zeros(k1)
                curr_midi_notes = {}
                for fft_fq in combination:
                    fq = fft_to_hz_array[fft_fq]
                    curr_midi_notes[hz_to_midi(fq)] = (
                        amplitude_sum[fft_fq] / len(patterns[fft_fq]))
                    result[fft_fq] = amplitude_sum[fft_fq]
                all_midi_notes.append(curr_midi_notes)
                all_results.append(result)
                all_patterns.append(harmonicsPattern)

            all_combinations.append(CombinationData(
                possible_combinations, all_saliences, all_midi_notes, all_results, all_patterns))

            resF0Weights.append(all_results[np.argmax(all_saliences)])
            resNotes.append(all_midi_notes[np.argmax(all_saliences)])
        return resNotes, resF0Weights, peaks, all_combinations

    def flatten_combination(all_combinations):
        new_saliences = []
        for frame in range(0, len(all_combinations)):
            (currCombs, _, curr_midi_notes, _, _) = all_combinations[frame]
            currnew_saliences = []
            for comb in range(0, len(currCombs)):
                new_salience = 0
                for k in range(-temporal__smoothness_range, temporal__smoothness_range + 1):
                    (_, neighbourall_saliences, neighbour_midi_notes, _,
                     _) = all_combinations[min(max(frame + k, 0), len(all_combinations) - 1)]
                    if curr_midi_notes[comb] in neighbour_midi_notes:
                        new_salience += neighbourall_saliences[neighbour_midi_notes.index(
                            curr_midi_notes[comb])]
                currnew_saliences.append(new_salience)
            new_saliences.append(currnew_saliences)
        return new_saliences

    def pitchTracking(all_combinations, saliences):
        """
        Implementacja przetwarzania końcowego w postaci
        śledzenia wysokości przedstawionego w pracy z 2012 roku
        """
        graph = nx.DiGraph()
        first_node = None
        last_node = None

        def count_weight(lvi, lvj, salience_j):
            D = 0
            fundamentals_i = map(lambda x: x[0], lvi)
            fundamentals_j = map(lambda x: x[0], lvj)
            for pattern_i in lvi:
                if pattern_i[0] in fundamentals_j:

                    D += np.abs(sum(map(lambda a: a[1], pattern_i[1])) + sum(
                        map(lambda a: a[1], [item for item in lvj if item[0] == pattern_i[0]][0][1])))
                else:
                    D += sum(map(lambda a: a[1], pattern_i[1]))
            for pattern_j in lvj:
                if pattern_j[0] not in fundamentals_i:
                    D += sum(map(lambda a: a[1], pattern_j[1]))
            return D / (salience_j + 1)

        for frame in range(0, len(all_combinations) - 1):
            (_, _, _, _, curr_patterns) = all_combinations[frame]
            (_, _, _, _, nextPatterns) = all_combinations[frame + 1]

            curr_frame_sorted = get_arg_max(saliences[frame])
            next_frame_sorted = get_arg_max(saliences[frame + 1])
            for curr_vertex in range(0, min(len(curr_patterns), pitch_tracking_combinations)):
                for next_frame_vertex in range(0, min(len(nextPatterns), pitch_tracking_combinations)):
                    graph.add_edge((frame, curr_frame_sorted[curr_vertex]), (frame + 1, next_frame_sorted[next_frame_vertex]),
                                   weight=count_weight(curr_patterns[curr_frame_sorted[curr_vertex]], nextPatterns[next_frame_sorted[next_frame_vertex]], saliences[frame + 1][next_frame_sorted[next_frame_vertex]]))
                    if first_node == None:
                        first_node = (frame, curr_frame_sorted[curr_vertex])
                    if frame + 1 == len(all_combinations) - 1:
                        last_node = (frame, curr_frame_sorted[curr_vertex])

        dijkstra_path = nx.dijkstra_path(
            graph, first_node, last_node, weight='weight')

        resNotes = []
        for edge in dijkstra_path:
            if edge is not None:
                resNotes.append(all_combinations[edge[0]][2][edge[1]])

        return dijkstra_path, graph, resNotes

    def pertus_and_inesta_2008():
        res_notes, res_f0_weights, peaks, _ = core_method()

        res_midi, res_piano_roll = post_process_midi_notes(res_notes)

        return res_midi, res_piano_roll, res_f0_weights, peaks, None, None

    def pertus_and_inesta_2012():
        res_notes, res_f0_weights, peaks, all_combinations = core_method()

        new_saliences = flatten_combination(all_combinations)

        dijkstra_path, graph, res_notes = pitchTracking(
            all_combinations, new_saliences)

        res_midi, res_piano_roll = post_process_midi_notes(res_notes)

        return res_midi, res_piano_roll, res_f0_weights, peaks, dijkstra_path, graph

    if new_algorithm_version:
        return pertus_and_inesta_2012()
    return pertus_and_inesta_2008()

## Funkcja do użytku serwera


def transcribe_by_generative_method_wrapped(filePath, newV, outPath):
    """
    Funkcja pomocnicza do wywołania głównej metody przez serwer
    """
    frame_width = 8192
    spacing = 1024
    sample_rate, data = loadNormalizedSoundFile(filePath)

    res_midi, _, _, _, _, _ = harmonic_and_smoothness_based_transcription(
        data, sample_rate, 4, frame_width, spacing, frame_width * 3, new_algorithm_version=newV)

    write_midi(res_midi, outPath)


if __name__ == "__main__":
    test_frame_width = 8192
    test_spacing = 1024
    test_filePath = path.dirname(path.abspath(__file__))
    test_filePath = path.join(
        test_filePath, '../test_sounds/Chopin_prelude28no.4inEm/chopin_prelude_28_4.wav')
    test_sample_rate, test_data = loadNormalizedSoundFile(test_filePath)
    test_data = test_data[:(int(len(test_data) / 12))]

    test_res_midi, test_res_piano_roll, test_res_f0_weights, test_peaks, test_path, test_graph = harmonic_and_smoothness_based_transcription(
        test_data, test_sample_rate, 4, test_frame_width, test_spacing, test_frame_width * 3, new_algorithm_version=False, disable_tqdm=False)

    write_midi(test_res_midi, "./generative_method_by_pertus_and_inestaTest.mid")
    plot_midi(test_res_piano_roll, test_spacing, test_sample_rate)
    plot_peaks(test_peaks, test_frame_width, test_sample_rate)
    plot_spectrogram(test_res_f0_weights, test_spacing, test_sample_rate)
