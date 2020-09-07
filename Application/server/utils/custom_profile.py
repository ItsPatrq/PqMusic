"""
W tym module znajdują się mechanizm mierzenia czasu wykonywania algorytmów
"""

import time
from functools import wraps

PROF_DATA = {}

def profile(fn):
    """
    Dekorator dodawany do klas w celu sprawdzania czasu wykonywania funkcji
    Ze względu na przyjętą postać argumentów funkcji,
    obliczana jest długość danych wejściowych
    """
    @wraps(fn)
    def with_profiling(normalized_data, sample_rate, *args, **kwargs):
        start_time = time.time()

        ret = fn(normalized_data, sample_rate, *args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, [], []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append((elapsed_time, len(normalized_data) / sample_rate))

        return ret

    return with_profiling

def print_normalize_profile_data(n=0, fc_name=""):
    """
    Funkcja wypisująca sformatowane dane o czasie
    działania funkcji z dekoratorem profile
    """
    res = ""
    for fname, data in PROF_DATA.items():
        if fc_name == "" or fname == fc_name:
            data[1].sort(key = lambda x: x[0])
            sortedByPow = data[1]
            if n > 0:
                sortedByPow = sortedByPow[n:]
                sortedByPow = sortedByPow[:-n]
            max_time = max(sortedByPow,key=lambda x: x[0])
            avg_time = sum(i for i, j in sortedByPow) / len(sortedByPow)
            data_time = sum(j for i, j in sortedByPow)
            avg_data_time = data_time / len(sortedByPow)
            fCalled = "Function %s called %d times. " % (fname, data[0])
            fData = "Execution time max: %.3f, average: %.3f" % (max_time[0], avg_time)
            processedTime = "Transcribed data had %.3f seconds, avg. %.3f seconds" %  (data_time, avg_data_time)
            res += fCalled + "\n" + fData + "\n" + processedTime + "\n"

    return res

def get_and_clear_prof_data(fcName):
    """
    Pobiera i czyści zapisane dane o czasie wykonywania
    """
    res = PROF_DATA[fcName]
    PROF_DATA[fcName] = [0, [], []]
    return res

def update_prof_data(fcName, profData):
    """
    Wymuszone aktualizowanie danych. Używane przy równoległuch obliczeniach
    """
    if fcName not in PROF_DATA:
        PROF_DATA[fcName] = [0, [], []]
    PROF_DATA[fcName][0] += profData[0]
    for data in profData[1]:
        PROF_DATA[fcName][1].append(data)

def clear_prof_data():
    """
    Wymuszone wyczyszczenie danych
    """
    global PROF_DATA
    PROF_DATA = {}
