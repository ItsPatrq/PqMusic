import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
import numpy as np

pycuda.driver.init()
dev = pycuda.driver.Device(0) # replace n with your device number
ctx = dev.make_context()

def gpu_example():
    a = np.ones(4000, dtype=np.float32)
    a_gpu = gpuarray.to_gpu(a)
    ans = (2 * a_gpu).get()
    return ans

# include your FFT code here
x = gpu_example()
print(x, len(x))
print("OH YEAH")
ctx.pop()
pycuda.tools.clear_context_caches()