import numpy as np
from scipy.fftpack import fft, ifft
import enum
from reikna import fft as cu_fft
from reikna.cluda import dtypes, cuda_api
from .cepstrumUtils import LifterType
from pycuda import cumath
class CepstrumUtilsGpu:
	def __init__(self, api, frameWidth):  
		self.api = api
		self.thr = api.Thread.create()
		self.frameWidth = frameWidth
		self.res_dev = self.thr.array((frameWidth,), dtype=np.complex64)
		self.hamming_dev = self.thr.to_device(np.hamming(frameWidth))
		self.fftc = cu_fft.FFT(self.res_dev).compile(self.thr)

	def real_cepst_from_signal(self, data):
		raise NotImplementedError("Is it even necessary?")
# 		data = np.array(data) + 0j
# 		dev_data = self.thr.to_device(data)
# 		dev_powerSp = self.thr.empty_like(dev_data)

# 		fft = cu_fft.FFT(dev_powerSp)
# 		fft_compiled = fft.compile(self.thr)
# 		fft_compiled(dev_powerSp, dev_data, inverse=0)
# #		self.fftc(dev_powerSp, dev_data, inverse=0)
# 		return dev_powerSp.__abs__().get()
# 		logSp = cumath.log(dev_data.__abs__())
# 		self.fftc(self.res_dev, logSp, inverse=1)
# 		return self.res_dev.get()
