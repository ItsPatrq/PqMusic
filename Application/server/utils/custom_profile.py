import time
from functools import wraps
import numpy as np

PROF_DATA = {}

def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling

def print_normalize_profile_data(n = 0, fc_name = ""):
    res = ""
    for fname, data in PROF_DATA.items():
        if fc_name == "" or fname == fc_name:
            sortedByPow = np.sort(data[1])
            if n > 0:
                sortedByPow = sortedByPow[n:]
                sortedByPow = sortedByPow[:-n]
            max_time = max(sortedByPow)
            avg_time = sum(sortedByPow) / len(sortedByPow)
            fCalled = "Function %s called %d times. " % (fname, data[0])
            fData = "Execution time max: %.3f, average: %.3f" % (max_time, avg_time)
            res += fCalled + "\n" + fData + "\n"
    return res
        
def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print("Function %s called %d times. " % (fname, data[0]),)
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}