"""
W tym module znajduje się implementacja algorytmu wykrywającego F0 przy pomocy metod cepstrum na GPU
"""

from reikna.cluda import cuda_api
import pycuda.tools
import pycuda.driver
import numpy as np

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.ceps_utils_gpu import CepsUtilsGpu # pylint: disable=import-error
from utils.plots import plot_cepstrogram # pylint: disable=import-error
from utils.general import loadNormalizedSoundFile # pylint: disable=import-error

## Analiza F0 przy pomocy cepstrum na GPU


def cepstrum_f0_analysis_gpu(thr, compiled_cepstrum, data, sample_rate=1024,\
    frame_width=512, spacing=512, size_of_zero_padding=512):
    """
    Funkcja wyznaczająca F0 sygnału przy pomocy cepstrum z użyciem GPU.
    Params:
        thr: wątek GPU
        compiled_cepstrum: instancja klasy CepsUtilsGpu do liczenia cepstrum na GPU ze skompilowanym planem
        data: sygnał wejściowy w postaci tablicy numpy
    Returns:
        best_fq: tablica wyznaczonych F0
        cepstra: tablica cepstrum kolejnych okien czasowych
        compiled_cepstrum: pomocnicza klasa do liczenia cepstrum na GPU ze skompilowanym planem
    """
    if compiled_cepstrum is None:
        params = dict(Fs=sample_rate, NFFT=frame_width, noverlap=frame_width -
                      spacing, pad_to=frame_width+size_of_zero_padding)
        compiled_cepstrum = CepsUtilsGpu(
            data, NFFT=params['NFFT'], noverlap=params['noverlap'],\
            pad_to=params['pad_to']).compile(thr)

    data_dev = thr.to_device(data)
    ceps_dev = thr.empty_like(compiled_cepstrum.parameter.output)
    compiled_cepstrum(ceps_dev, data_dev)
    cepstra = ceps_dev.get()
    best_fq = []
    for cepst in cepstra.T:
        maxperiod = np.argmax(cepst)
        if maxperiod == 0:
            best_fq.append(0)
        else:
            best_fq.append(sample_rate/maxperiod)
    return cepstra, best_fq, compiled_cepstrum


if __name__ == "__main__":
    test_frame_width = 2048
    test_spacing = 512
    test_filePath = path.dirname(path.abspath(__file__))
    test_filePath = path.join(
        test_filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')

    test_sample_rate, test_data = loadNormalizedSoundFile(test_filePath)

    pycuda.driver.init()  # pylint: disable=no-member
    test_dev = pycuda.driver.Device(0)  # pylint: disable=no-member
    test_ctx = test_dev.make_context()
    test_api = cuda_api()
    test_thr = test_api.Thread.create()

    test_compiled_cepstrum = None

    test_cepstra, test_best_fq, test_compiled_cepstrum = cepstrum_f0_analysis_gpu(
        test_thr, test_compiled_cepstrum, np.array(test_data), test_sample_rate, 4096, 1024, 8192)

    plot_cepstrogram(test_cepstra, test_spacing, test_sample_rate,
                     transpose=False, showColorbar=False)

    test_ctx.pop()
    pycuda.tools.clear_context_caches()
