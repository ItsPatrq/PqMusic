import time
from functools import wraps
import numpy as np

PROF_DATA = {}

def profile(fn):
    @wraps(fn)
    def with_profiling(normalizedData, sampleRate, *args, **kwargs):
        start_time = time.time()

        ret = fn(normalizedData, sampleRate, *args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, [], []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append((elapsed_time, len(normalizedData) / sampleRate))

        return ret

    return with_profiling

def profile_old(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, [], []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling

def print_normalize_profile_data_old(n = 0, fc_name = ""):
    res = ""
    for fname, data in PROF_DATA.items():
        if fc_name == "" or fname == fc_name:
            data[1].sort()
            sortedByPow = data[1]
            if n > 0:
                sortedByPow = sortedByPow[n:]
                sortedByPow = sortedByPow[:-n]
            max_time = max(sortedByPow)
            avg_time = sum(sortedByPow) / len(sortedByPow)
            fCalled = "Function %s called %d times. " % (fname, data[0])
            fData = "Execution time max: %.3f, average: %.3f" % (max_time, avg_time)
            res += fCalled + "\n" + fData + "\n" 

    return res

def print_normalize_profile_data(n = 0, fc_name = ""):
    res = ""
    for fname, data in PROF_DATA.items():
        if fc_name == "" or fname == fc_name:
            data[1].sort(key = lambda x: x[0])
            sortedByPow = data[1]
            if n > 0:
                sortedByPow = sortedByPow[n:]
                sortedByPow = sortedByPow[:-n]
            max_time = max(sortedByPow,key=lambda x:x[0])
            avg_time = sum(i for i, j in sortedByPow) / len(sortedByPow)
            data_time = sum(j for i, j in sortedByPow)
            avg_data_time = data_time / len(sortedByPow)
            fCalled = "Function %s called %d times. " % (fname, data[0])
            fData = "Execution time max: %.3f, average: %.3f" % (max_time[0], avg_time)
            processedTime = "Transcribed data had %.3f seconds, avg. %.3f seconds" %  (data_time, avg_data_time)
            res += fCalled + "\n" + fData + "\n" + processedTime + "\n"

    return res
        
def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print("Function %s called %d times. " % (fname, data[0]),)
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))

def get_and_clear_prof_data(fcName):
    res = PROF_DATA[fcName]
    PROF_DATA[fcName] = [0, [], []]
    return res

def update_prof_data(fcName, profData):
    if fcName not in PROF_DATA:
        PROF_DATA[fcName] = [0, [], []]
    PROF_DATA[fcName][0] += profData[0]
    for data in profData[1]:
        PROF_DATA[fcName][1].append(data)

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}