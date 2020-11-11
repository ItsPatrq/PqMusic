"""
W tym module znajduje się implementacja algorytmu wykrywającego F0 przy pomocy metod cepstrum na CPU
"""

import numpy as np
import math
from io import BytesIO

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.cepstrum_utils import real_cepst_from_signal  # pylint: disable=import-error
from utils.plots import plot_spectrum_line_component_only, plot_spectrogram, plot_cepstrogram, plot_pitches  # pylint: disable=import-error
from utils.general import loadNormalizedSoundFile  # pylint: disable=import-error

def cepstrum_f0_analysis(data, sample_rate=1024, frame_width=512, spacing=512, size_of_zero_padding=512):
    """
    Funkcja wyznaczająca F0 sygnału przy pomocy cepstrum. Dzieli dane wejściowe na okna czasowe,na których
    wyliczane jest cepstrum a następnie zwracany indeks największej wartości cepstrum
    jako F0 danego okna.
    Returns:
        best_fq: tablica wyznaczonych F0
        correlogram: korelogram
        cepstra: tablica cepstrum kolejnych okien czasowych
        spectrogram: spektrogram sygnału wejściowego
        log_spectrogram: spektrogram logarytmu mocy sygnału wejściowego
    """
    hanning = np.hanning(frame_width)
    spectrogram = []
    log_spectrogram = []
    cepstra = []
    best_fq = []
    zero_padding = np.zeros(size_of_zero_padding)

    for i in range(0, int(math.ceil((len(data) - frame_width) / spacing))):
        frame = data[i*spacing:i*spacing+frame_width]
        frame = frame*hanning
        frame = np.concatenate((frame, zero_padding))
        cepst, log_sp, spectr = real_cepst_from_signal(frame)
        fft_len = int(np.floor(len(spectr)/2))
        spectrogram.append(np.abs(spectr[:fft_len]))
        log_spectrogram.append(log_sp[:fft_len])
        cepst = cepst[:fft_len//2]
        cepst[0:14] = np.zeros(14)
        cepstra.append(cepst)

        maxperiod = np.argmax(cepst)
        best_fq.append(sample_rate/maxperiod)

    return best_fq, cepstra, spectrogram, log_spectrogram
## Funkcja do użytku serwera


def transcribe_by_cepstrum_wrapped(filePath):
    """
    Funkcja pomocnicza do wywołania głównej metody przez serwer
    """
    frame_width = 2048
    spacing = 512
    sample_rate, data = loadNormalizedSoundFile(filePath)
    best_fq, cepstra, spectra, log_spectrogram = cepstrum_f0_analysis(
        data, sample_rate, frame_width, spacing, frame_width)

    fig, _ = plot_pitches(best_fq, spacing, sample_rate,
                          show=False, language="eng")
    fig2, _ = plot_cepstrogram(
        cepstra, spacing, sample_rate, show=False, language="eng")
    fig3, _ = plot_spectrogram(
        spectra, spacing, sample_rate, show=False, language="eng")
    fig4, _ = plot_spectrogram(log_spectrogram, spacing, sample_rate,
                               show=False, language="eng", title="logPowSpectrogram")

    pitches, cepstrogram, spectrogram, log_spectrogram = BytesIO(
    ), BytesIO(), BytesIO(), BytesIO()
    fig.savefig(pitches, format="png")
    fig2.savefig(cepstrogram, format="png")
    fig3.savefig(spectrogram, format="png")
    fig4.savefig(log_spectrogram, format="png")

    return pitches, cepstrogram, spectrogram, log_spectrogram


if __name__ == "__main__":
    test_frame_width = 2048
    test_spacing = 512
    test_filePath = path.dirname(path.abspath(__file__))
    test_filePath = path.join(test_filePath,
                              '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    test_sample_rate, test_data = loadNormalizedSoundFile(test_filePath)

    test_best_fq, test_cepstra, test_spectra, test_log_spectrogram =\
        cepstrum_f0_analysis(test_data, test_sample_rate, 4096, 1024, 8192)

    plot_spectrum_line_component_only(
        test_spectra[5], test_sample_rate, language="pl")
