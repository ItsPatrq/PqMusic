"""
W tym module znajduje się implementacja autokorelacji operującej na sygnale audio w domenie czasu
"""

from io import BytesIO
from math import ceil, floor
from tqdm import tqdm
import numpy as np

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.plots import plot_pitches, plot_correlogram # pylint: disable=import-error
from utils.general import loadNormalizedSoundFile # pylint: disable=import-error

def autocorrelation(data, sample_rate, frame_width, spacing, fq_min, fq_max, disable_tqdm=True):
    """
    Główna funkcja autokorelacji. Dzieli dane wejściowe na okna czasowe, na których wykonuje autokorelacje
    na zadanym przedziale.
    Returns:
        best_fq: Tablica wyznaczonych F0
        correlogram: korelogram
    """
    def ac(curr_frame, min_lag, max_lag):
        res = list(np.zeros(min_lag))
        n = len(curr_frame)
        for lag in range(min_lag, max_lag):
            ac_result = np.zeros(n+lag)
            ac_result[:n] = curr_frame
            ac_result[:n-lag] *= curr_frame[lag:]
            ac_sum = np.sum(ac_result[:n-lag])
            res.append(ac_sum/(n-lag))
        return res

    best_fq = []
    correlogram = []
    hann = np.hanning(frame_width)
    min_lag = int(floor(sample_rate / fq_max))
    max_lag = int(ceil(sample_rate / fq_min))

    for i in tqdm(range(0, int(ceil((len(data) - frame_width) / spacing))), disable=disable_tqdm):
        frame = data[i*spacing:i*spacing+frame_width] * hann
        res = ac(frame, min_lag, max_lag)
        correlogram.append(res)
        bestLag = np.argmax(res)
        best_fq.append(0 if bestLag < min_lag else sample_rate/bestLag)

    return best_fq, correlogram

def autocorrelation_wrapped(file_path):
    """
    Funkcja pomocnicza do wywołania głównej metody przez serwer
    """
    fq_min = 50
    fq_max = 2000
    frame_width = 2048
    spacing = 2048
    sample_rate, data = loadNormalizedSoundFile(file_path)
    best_frequencies, correlogram = autocorrelation(
        data, sample_rate, frame_width, frame_width, fq_min, fq_max)
    fig, _ = plot_pitches(best_frequencies, spacing,
                          sample_rate, show=False, language="eng")
    fig2, _ = plot_correlogram(
        correlogram, spacing, sample_rate, show=False, language="eng")
    pitches, correlogram = BytesIO(), BytesIO()
    fig.savefig(pitches, format="png")
    fig2.savefig(correlogram, format="png")
    return pitches, correlogram


if __name__ == "__main__":
    test_fq_min = 50
    test_fq_max = 2000
    test_frame_width = 2048
    test_spacing = 2048

    test_file_path = path.dirname(path.abspath(__file__))
    test_file_path = path.join(
        test_file_path, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    test_sample_rate, test_data = loadNormalizedSoundFile(test_file_path)

    test_best_frequencies, test_correlogram = autocorrelation(
        test_data, test_sample_rate, test_frame_width, test_frame_width, test_fq_min, test_fq_max, disable_tqdm=False)

    plot_pitches(test_best_frequencies, test_spacing, test_sample_rate, language="pl")
    plot_correlogram(test_correlogram, test_spacing, test_sample_rate, language="pl")
