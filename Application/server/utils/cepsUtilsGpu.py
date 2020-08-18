## W tym pliku znajdują się funkcje liczące cepstrum przy pomocy GPU

import numpy

from reikna.cluda import any_api
from reikna.cluda import dtypes, functions
from reikna.core import Computation, Transformation, Parameter, Annotation, Type
from reikna.fft import FFT
from reikna.algorithms import Transpose
import reikna.transformations as transformations


def hanning_window(arr, NFFT):
    """
    Applies Hann window to the rows of a 2D array.
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
        connectors=['output'])

def log_pow(arr_t):
    """
    Returns log(abs(arr))
    """

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

def crop_frequencies_ceps(arr):
    """
    Nyquist Frequency / 2(because of cepst not spec) + zeroing first 10 cep values 
    """
    out_dtype = dtypes.real_for(arr.dtype)
    result_arr = Type(out_dtype, (arr.shape[0], arr.shape[1] // 4 + 1))
    return Transformation(
        [
            Parameter('output', Annotation(result_arr, 'o')),
            Parameter('input', Annotation(arr, 'i'))],
        """
        if (${idxs[1]} < ${input.shape[1] // 4 + 1}){
            ${input.ctype} val = ${input.load_same};
            
            ${output.ctype} norm = ${norm}(val);
            if (${idxs[1]} < ${10}) {
                norm = norm * 0;
            }
            ${output.store_same}(norm);
        }
        """,
        render_kwds=dict(
            norm=functions.norm(arr.dtype),
            ),
            connectors=['input'])

# pylint: disable=no-member
class CepsUtilsGpu(Computation):
 
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
        log_pow_trf = log_pow(fft_arr)
 
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

        fft.parameter.output.connect(
            log_pow_trf, log_pow_trf.input, log_pow=log_pow_trf.output)


        ifft = FFT(Type(complex_dtype, fft.parameter.log_pow.shape), axes=(1,))
        ifft.parameter.input.connect(
            to_complex_trf, to_complex_trf.output,
            input_real=to_complex_trf.real, input_imag=to_complex_trf.imag)

        ifft.parameter.input_imag.connect(
            broadcast_zero_trf, broadcast_zero_trf.output)


        crop_trf = crop_frequencies_ceps(ifft.parameter.output)

        ifft.parameter.output.connect(
            crop_trf, crop_trf.input, cropped_amplitude=crop_trf.output)
 
        self._fft = fft
        self._ifft = ifft
        self._transpose = Transpose(ifft.parameter.cropped_amplitude)
 
        Computation.__init__(self,
            [Parameter('output', Annotation(self._transpose.parameter.output, 'o')),
            Parameter('input', Annotation(fft.parameter.flat_input, 'i'))
            ])
 
    def _build_plan(self, plan_factory, device_params, output, input_):
        plan = plan_factory()
        temp = plan.temp_array_like(self._fft.parameter.log_pow)
        temp2 = plan.temp_array_like(self._ifft.parameter.cropped_amplitude)
        plan.computation_call(self._fft, temp, input_)
        plan.computation_call(self._ifft, temp2, temp, 1)

        plan.computation_call(self._transpose, output, temp2)
        return plan
