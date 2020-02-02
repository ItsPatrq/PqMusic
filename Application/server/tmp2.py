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

from utils.plots import plot_spectrogram, plot_cepstrogram
from transcription.cepstrumF0Analysis import cepstrumF0Analysis

def hanning_window(arr, NFFT):
    """
    Applies the von Hann window to the rows of a 2D array.
    To account for zero padding (which we do not want to window), NFFT is provided separately.
    """
    if dtypes.is_complex(arr.dtype):
        coeff_dtype = dtypes.real_for(arr.dtype)
    else:
        coeff_dtype = arr.dtype
    return Transformation(
        [
            Parameter('output', Annotation(arr, 'o')),
            Parameter('input', Annotation(arr, 'i')),
        ],
        """
        ${dtypes.ctype(coeff_dtype)} coeff;
        %if NFFT != output.shape[0]:
        if (${idxs[1]} >= ${NFFT})
        {
            coeff = 1;
        }
        else
        %endif
        {
            coeff = 0.5 * (1 - cos(2 * ${numpy.pi} * ${idxs[-1]} / (${NFFT} - 1)));
        }
        ${output.store_same}(${mul}(${input.load_same}, coeff));
        """,
        render_kwds=dict(
            coeff_dtype=coeff_dtype, NFFT=NFFT,
            mul=functions.mul(arr.dtype, coeff_dtype)))


def rolling_frame(arr, NFFT, noverlap, pad_to):
    """
    Transforms a 1D array to a 2D array whose rows are
    partially overlapped parts of the initial array.
    """

    frame_step = NFFT - noverlap
    frame_num = (arr.size - noverlap) // frame_step
    frame_size = NFFT if pad_to is None else pad_to

    result_arr = Type(arr.dtype, (frame_num, frame_size))

    return Transformation(
        [
            Parameter('output', Annotation(result_arr, 'o')),
            Parameter('input', Annotation(arr, 'i')),
        ],
        """
        %if NFFT != output.shape[1]:
        if (${idxs[1]} >= ${NFFT})
        {
            ${output.store_same}(0);
        }
        else
        %endif
        {
            ${output.store_same}(${input.load_idx}(${idxs[0]} * ${frame_step} + ${idxs[1]}));
        }
        """,
        render_kwds=dict(frame_step=frame_step, NFFT=NFFT),
        # note that only the "store_same"-using argument can serve as a connector!
        connectors=['output'])

def log_pow(arr_t):
    if dtypes.is_complex(arr_t.dtype):
        out_dtype = dtypes.real_for(arr_t.dtype)
    else:
        out_dtype = arr_t.dtype

    return Transformation(
        [
            Parameter('output', Annotation(Type(out_dtype, arr_t.shape), 'o')),
            Parameter('input', Annotation(arr_t, 'i'))],
        """
        ${input.ctype} val = ${input.load_same};
        ${output.ctype} norm = ${norm}(val);
        norm = log(norm) / 2;
        ${output.store_same}(norm);
        """,
        render_kwds=dict(
            norm=functions.norm(arr_t.dtype),
            ))

def crop_frequencies(arr):
    """
    Crop a 2D array whose columns represent frequencies to only leave the frequencies with
    different absolute values.
    """
    result_arr = Type(arr.dtype, (arr.shape[0], arr.shape[1] // 2 + 1))
    return Transformation(
        [
            Parameter('output', Annotation(result_arr, 'o')),
            Parameter('input', Annotation(arr, 'i')),
        ],
        """
        if (${idxs[1]} < ${input.shape[1] // 2 + 1})
            ${output.store_idx}(${idxs[0]}, ${idxs[1]}, ${input.load_same});
        """,
        # note that only the "load_same"-using argument can serve as a connector!
        connectors=['input'])

def crop_frequencies_ceps(arr):
    """
    Crop a 2D array whose columns represent frequencies to only leave the frequencies with
    different absolute values.
    """
    out_dtype = dtypes.real_for(arr.dtype)
    result_arr = Type(out_dtype, (arr.shape[0], arr.shape[1] // 2 + 1))
    return Transformation(
        [
            Parameter('output', Annotation(result_arr, 'o')),
            Parameter('input', Annotation(arr, 'i')),
        ],
        """
        if (${idxs[1]} < ${input.shape[1] // 2 + 1}){
            ${input.ctype} val = ${input.load_same};
            ${output.ctype} norm = ${norm}(val.x);
            if (${idxs[1]} < ${10}) {
                norm = ${norm}(0);
            }
            ${output.store_same}(norm);
        }

        """,
        # note that only the "load_same"-using argument can serve as a connector!
        render_kwds=dict(
            norm=functions.norm(result_arr),
            ),
        connectors=['input'])
# pylint: disable=no-member
class Spectrogram(Computation):
 
    def __init__(self, x, NFFT=256, noverlap=128, pad_to=None, window=hanning_window):
 
        assert dtypes.is_real(x.dtype)
        assert x.ndim == 1
 
        rolling_frame_trf = rolling_frame(x, NFFT, noverlap, pad_to)
 
        complex_dtype = dtypes.complex_for(x.dtype)
        fft_arr = Type(complex_dtype, rolling_frame_trf.output.shape)
        real_fft_arr = Type(x.dtype, rolling_frame_trf.output.shape)
 
        window_trf = window(real_fft_arr, NFFT)
        broadcast_zero_trf = transformations.broadcast_const(real_fft_arr, 0)
        to_complex_trf = transformations.combine_complex(fft_arr)
        #amplitude_trf = transformations.norm_const(fft_arr, 1)
        log_pow_trf = log_pow(fft_arr)
        crop_trf = crop_frequencies(log_pow_trf.output)

        fft = FFT(fft_arr, axes=(1,))
        fft.parameter.input.connect(
            to_complex_trf, to_complex_trf.output,
            input_real=to_complex_trf.real, input_imag=to_complex_trf.imag)

        fft.parameter.input_imag.connect(
            broadcast_zero_trf, broadcast_zero_trf.output)

        fft.parameter.input_real.connect(
            window_trf, window_trf.output, unwindowed_input=window_trf.input)

        fft.parameter.unwindowed_input.connect(
            rolling_frame_trf, rolling_frame_trf.output, flat_input=rolling_frame_trf.input)

        # fft.parameter.output.connect(
        #     amplitude_trf, amplitude_trf.input, amplitude=amplitude_trf.output)

        fft.parameter.output.connect(
            log_pow_trf, log_pow_trf.input, log=log_pow_trf.output)

        fft.parameter.log.connect(
            crop_trf, crop_trf.input, cropped_amplitude=crop_trf.output)
 
        self._fft = fft
        self._transpose = Transpose(fft.parameter.cropped_amplitude)
 
        Computation.__init__(self,
            [Parameter('output', Annotation(self._transpose.parameter.output, 'o')),
            Parameter('input', Annotation(fft.parameter.flat_input, 'i'))])
 
    def _build_plan(self, plan_factory, device_params, output, input_):
        plan = plan_factory()
        temp = plan.temp_array_like(self._fft.parameter.cropped_amplitude)
        plan.computation_call(self._fft, temp, input_)

        plan.computation_call(self._transpose, output, temp)
        return plan

if __name__ == '__main__':
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, 'test_sounds/piano-c3-d3-c3-b2.wav')
    sampleRate, data = loadNormalizedSoundFIle(filePath)

    fake_params = dict(Fs=sampleRate, NFFT=1024, noverlap=512, pad_to=2048)
    
    x = data
    params = fake_params


    cepstra, spectra, bestFq = cepstrumF0Analysis(data, sampleRate, 1024, 1024, 512)

    api = any_api()
    thr = api.Thread.create()

    specgram_reikna = Spectrogram(
        x, NFFT=params['NFFT'], noverlap=params['noverlap'], pad_to=params['pad_to']).compile(thr)

    x_dev = thr.to_device(x)
    spectre_dev = thr.empty_like(specgram_reikna.parameter.output)
    specgram_reikna(spectre_dev, x_dev)
    spectre_reikna = spectre_dev.get()
    print('!!!!!!', numpy.min(spectre_reikna))

    #assert numpy.allclose(spectre, spectre_reikna)
    #plot_spectrogram(spectre_reikna, 1024 - 900, sampleRate, transpose=False)
    plot_spectrogram(spectre_reikna, 512, sampleRate, transpose=False)
    plot_spectrogram(spectra, 512, sampleRate)



