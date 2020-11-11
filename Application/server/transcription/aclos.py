"""
W tym module znajduje się implementacja algorytmu ACLOS
"""

import numpy as np
from scipy.fftpack import fft
from scipy.interpolate import interp1d
from tqdm import tqdm
import math
from io import BytesIO

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.cepstrum_utils import lifter_on_power_spec, LifterType  # pylint: disable=import-error
from utils.plots import plot_spectrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation  # pylint: disable=import-error
from utils.general import loadNormalizedSoundFile, fft_to_hz  # pylint: disable=import-error

def aclos(data, sample_rate=1024, frame_width=512, spacing=512,
          size_of_zero_padding=512, disable_tqdm=True):
    """
    Funkcja autokorelacji na spektrum mocy wyznaczająca F0. Dzieli dane wejściowe na okna czasowe,na których
    wykonywane jest spektrum mocy oraz liczona autokorelacja
    Returns:
        best_fq: Tablica wyznaczonych F0
        correlogram: korelogram
        interpolated_autocorrelogram: interpolacja korelogramu, z którego wyliczone były wynikowe F0
    """
    correlogram = []
    interpolated_autocorrelogram = []
    spectra = []
    best_fq = []
    liftered_spectra = []
    hann = np.hanning(frame_width)
    zero_padding = np.zeros(size_of_zero_padding)
    fft_to_fq = fft_to_hz(sample_rate, frame_width)
    fq_max_error = sample_rate // frame_width

    def autocorrelation(data, min_lag, max_lag):
        """
        Funkcja licząca autokorelacje dla $dane z maksymalnym/minimalnym
        przesunięciem równym odpowiednio $min_lag i max_lag
        """
        data_len = len(data)
        result = list(np.zeros(min_lag))
        for lag in range(min_lag, max_lag):
            sum_array = np.zeros(data_len + lag)
            sum_array[:data_len] = data
            sum_array[:data_len-lag] *= data[lag:]
            sum_from_array = np.sum(sum_array[:data_len-lag])
            result.append(float(sum_from_array/(data_len-lag)))

        interpolated = interp1d(
            np.arange(0, len(result)), result, kind='cubic')
        return result, interpolated

    def count_best_fq(interpolated_autocorrelation, data_len, interpol_multiplier=10):
        """
        Funkcja wyznaczająca częstotliwość F0 na podstawie
        interpolacji korelogramu
        """
        interp_x = np.linspace(0, data_len-1, num=data_len*interpol_multiplier)
        argmax = np.argmax(interpolated_autocorrelation(interp_x))
        correlation_arg_max = int(np.round(argmax / interpol_multiplier))
        delta = argmax - (correlation_arg_max * interpol_multiplier)
        best_fq = fft_to_fq[correlation_arg_max] + \
            (fq_max_error * delta / interpol_multiplier)
        return best_fq

    for i in tqdm(range(0, int(math.ceil((len(data) - frame_width) / spacing))),
                  disable=disable_tqdm):
        frame = data[i*spacing:i*spacing+frame_width] * hann
        frame = np.concatenate((frame, zero_padding))
        frame_complex = fft(frame)
        fft_len = int(np.floor(len(frame_complex)/2))
        powerSpec = abs(frame_complex)
        liftered_power_spec = lifter_on_power_spec(
            powerSpec, LifterType.sine, 8)

        powerSpec = powerSpec[:fft_len]
        liftered_power_spec = liftered_power_spec[:fft_len]

        autocorrelation_result, interpolated_autocorrelation = autocorrelation(
            liftered_power_spec, 5, frame_width // 2 + 1)

        correlogram.append(autocorrelation_result,)
        interpolated_autocorrelogram.append(interpolated_autocorrelation)
        spectra.append(powerSpec)
        liftered_spectra.append(liftered_power_spec)
        best_fq.append(count_best_fq(
            interpolated_autocorrelation, len(autocorrelation_result)))

    return best_fq, correlogram, interpolated_autocorrelogram, spectra


def transcribe_by_aclos_wrapped(file_path):
    """
    Funkcja pomocnicza do wywołania głównej metody przez serwer
    """
    frame_width = 2048
    spacing = 512
    sample_rate, data = loadNormalizedSoundFile(file_path)
    best_fq, correlogram, _, spectra = aclos(
        data, sample_rate, frame_width, spacing, frame_width)

    fig, _ = plot_pitches(best_fq, spacing, sample_rate,
                          show=False, language="eng")
    fig2, _ = plot_spectrogram(
        spectra, spacing, sample_rate, show=False, language="eng")
    fig3, _ = plot_correlogram(
        correlogram, spacing, sample_rate, show=False, language="eng")

    pitches_fig, correlogram_fig, spectrogram_fig = BytesIO(), BytesIO(), BytesIO()
    fig.savefig(pitches_fig, format="png")
    fig2.savefig(spectrogram_fig, format="png")
    fig3.savefig(correlogram_fig, format="png")

    return pitches_fig, correlogram_fig, spectrogram_fig


if __name__ == "__main__":
    test_frame_width = 2048
    test_spacing = 512
    test_file_path = path.dirname(path.abspath(__file__))
    test_file_path = path.join(
        test_file_path, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    test_sample_rate, test_data = loadNormalizedSoundFile(test_file_path)

    test_best_fq, test_correlogram, test_interpolated_autocorrelogram, test_spectra =\
        aclos(test_data, test_sample_rate, test_frame_width,
              test_spacing, test_frame_width, disable_tqdm=False)
    plot_interpolated_correlation(
        test_interpolated_autocorrelogram[10], test_correlogram[10], language='pl')
