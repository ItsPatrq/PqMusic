import numpy

import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.mlab import specgram

from reikna.cluda import any_api
from reikna.cluda import dtypes, functions
from reikna.core import Computation, Transformation, Parameter, Annotation, Type
from reikna.fft import FFT
from reikna.algorithms import Transpose
import reikna.transformations as transformations
from os import path
from utils.general import loadNormalizedSoundFIle
from pycuda import cumath
import pycuda
from utils.plots import plot_spectrogram, plot_cepstrogram, plot_wave
import pycuda.driver as cuda



if __name__ == '__main__':
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, 'test_sounds/single_tone.wav')
    #file_path = '../test_sounds/Sine_sequence.wav'
    #filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)
    plot_wave(sampleRate, data * 2, "name")
    # fake_params = dict(Fs=sampleRate, NFFT=1024, noverlap=512, pad_to=2048)
    # numpy.random.seed(125)

    # api = any_api()
    # thr = api.Thread.create()

    # a = numpy.random.randn(4,4)
    # a = a.astype(numpy.float32)

    # a_dev = cuda.mem_alloc(a.nbytes)
    # cuda.memcpy_htod(a_dev, a)

    # mod = pycuda.compiler.SourceModule("""
    #     __global__ void doublify(float *a)
    #     {
    #         int idx = threadIdx.x + threadIdx.y * 4;
    #         a[idx] *= 2;
    #     }
    # """)
    # func = mod.get_function("doublify")
    # func(a_dev, block=(4,4,1))
    # a_doubled = numpy.empty_like(a)
    # cuda.memcpy_dtoh(a_doubled, a_dev)
    # print(a_doubled)
    # print(a)