"""
W tym module znajduje się mechanizm ewaluacji algorytmów
"""

from datetime import datetime
import os
from random import uniform
import concurrent.futures
import json
import enum
import pycuda.driver
from itertools import product
from reikna.cluda import cuda_api

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utils.custom_profile import profile, print_normalize_profile_data, get_and_clear_prof_data, update_prof_data # pylint: disable=import-error
from general import loadNormalizedSoundFile # pylint: disable=import-error
from midi import load_midi_file, compare_midi_to_ground_truth, res_in_hz_to_midi_notes, write_midi # pylint: disable=import-error
from transcription.autocorrelation import autocorrelation # pylint: disable=import-error
from transcription.aclos import aclos # pylint: disable=import-error
from transcription.cepstrum_f0_analysis import cepstrum_f0_analysis # pylint: disable=import-error
from transcription.cepstrum_f0_analysis_gpu import cepstrum_f0_analysis_gpu # pylint: disable=import-error
from transcription.generative_method_by_pertus_and_inesta import harmonic_and_smoothness_based_transcription # pylint: disable=import-error
from transcription.onsets_and_frames import OnsetsAndFramesImpl # pylint: disable=import-error

audio_file = "audio_filename"
midi_file = "midi_filename"
split = "split"
canonical_title = "canonical_title"

max_error = 0.085


# Definiowanie możliwych argumentów, jakie mogą przyjmować poszczególne algorytmy
# do wyliczenia najlepszych argumentów dla danych algorytmów
# region możliwe argumenty
stdFrameWidth = [1024, 2048, 4096, 12288]
stdSpacing = [512, 1024]
stdZeroPadding = [12288, 12288]
stdMinF0 = [50, 75]
stdMaxF0 = [4000, 5500]
stdNeighbourMerging = [1, 3, 4]

argsAc = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'fqMin': stdMinF0,
    'fqMax': stdMaxF0
}

argsAclos = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding
}

argscepstrum_f0_analysis = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding
}

argsGenerativeMethodByPertusaAndInesta2008 = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6, 8],
    'relevantPowerThreashold': [4, 2],
    'maxInharmonyDegree': [0.11, 0.22, 0.32],
    'minHarmonicsPerCandidate': [1, 2, 3],
    'maxHarmonicsPerCandidate': [6, 8],
    'maxCandidates': [6, 8],
    'maxParallelNotes': [6, 8],
    'gamma': [0.1, 0.08],
    'minNoteMs': [55.68],
    'lifteringCoefficient': [0, 6],
    'minNoteVelocity': [16],
    'newAlgorithmVersion': [False],
    'smoothnessImportance': [None],
    'temporalSmoothnessRange': [None],
    'pitch_tracking_combinations': [None]
}

argsGenerativeMethodByPertusaAndInesta2012 = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6, 8],
    'relevantPowerThreashold': [4, 2],
    'maxInharmonyDegree': [0.11, 0.22, 0.32],
    'minHarmonicsPerCandidate': [1, 2, 3],
    'maxHarmonicsPerCandidate': [6, 8],
    'maxCandidates': [6, 8],
    'maxParallelNotes': [6, 8],
    'gamma': [0.1, 0.08],
    'minNoteMs': [55.68],
    'lifteringCoefficient': [0, 6],
    'minNoteVelocity': [16],
    'newAlgorithmVersion': [True],
    'smoothnessImportance': [3, 2],
    'temporalSmoothnessRange': [2, 3],
    'pitch_tracking_combinations': [3, 4]
}
# endregion możliwe argumenty

# region Wcześniej wyliczone najlepsze parametry dla algorytmów
best_arg_ac = (1, 1024, 1024, 50, 5500)
best_arg_aclos = (3, 4096, 1024, 2048)
best_arg_ceps = (3, 4096, 1024, 8192)
best_arg_Generative2008 = (3, 2048, 512, 8192, 50, 5500, 8, 2,
                           0.32, 1, 8, 6, 1, 0.1, 55, 0, 16, False, None, None, None)
best_arg_Generative2012 = (3, 2048, 512, 12288, 50, 5500, 8, 4,
                           0.22, 1, 8, 7, 5, 0.1, 55, 8, 16, True, 3, 2, 4)
best_arg_Generative2008_poli = (3, 2048, 512, 12288, 50, 5500, 6,
                                2, 0.22, 1, 8, 7, 7, 0.1, 55, 6, 16, False, None, None, None)
best_arg_Generative2012_poli = (3, 2048, 512, 12288, 50, 5500,
                                6, 2, 0.22, 1, 6, 6, 5, 0.1, 55, 6, 16, True, 3, 2, 4)
# endregion Wcześniej wyliczone najlepsze parametry dla algorytmów


class SplitEnum(enum.Enum):
    test = "test"
    train = "train"
    validation = "validation"


class F1Results:
    """
    Klasa pomocnicza do uporządkowania wyników ewaluacji
    """

    def __init__(self, FN, FP, TP, F1, percision, recall, accuracy, algorithm):
        self.FN = FN
        self.FP = FP
        self.TP = TP
        self.F1 = F1
        self.percision = percision
        self.recall = recall
        self.accuracy = accuracy
        self.algorithm = algorithm

    def print_results(self):
        return "Function name: " + self.algorithm + "\nNumber of tests: " + str(len(self.FN)) +\
            "\nAvarage FN: " + str(sum(self.FN) / len(self.FN)) + "\nAvarage FP: " + str(sum(self.FP) / len(self.FP)) +\
            "\nAvarage TP: " + str(sum(self.TP) / len(self.TP)) + "\nAvarage F1: " + str(sum(self.F1) / len(self.F1)) +\
            "\nAvarage percision: " + str(sum(self.percision) / len(self.percision)) + "\nAvarage recall: " + str(sum(self.recall) / len(self.recall)) +\
            "\nAvarage accuracy: " + str(sum(self.accuracy) / len(self.accuracy)) +\
            "\nTime estimation: " + \
            print_normalize_profile_data(5, self.algorithm)


class EvalObject:
    """
    Klasa pomocnicza do ustrukturyzowania obiektów testowych/ewaluacyjnych
    """

    def __init__(self, curr_audio_file, curr_midi_file, curr_split, curr_data_set_path, curr_audio_name):
        self.audio = curr_audio_file
        self.midi = curr_midi_file
        self.split = curr_split
        self.data_set_path = curr_data_set_path
        self.audio_name = curr_audio_name

    def test_method(self, method, max_error, save_dist=None):
        gtNotes = load_midi_file(self.get_midi_path())
        sample_rate, normalizedData = loadNormalizedSoundFile(
            self.get_audio_path())
        evalNotes = method(normalizedData, sample_rate)
        if save_dist != None:
            write_midi(evalNotes, save_dist)
        return compare_midi_to_ground_truth(evalNotes, gtNotes, max_error)

    def get_audio_path(self):
        return path.join(self.data_set_path, self.audio)

    def get_midi_path(self):
        return path.join(self.data_set_path, self.midi)


def load_metadata(dataSet):
    """
    Wczytanie metadanych wskazanego dataSetu
    """
    filePath = path.dirname(path.abspath(__file__))
    data_set_path = path.join(filePath, '../test_sounds/data_sets/', dataSet)
    jsonFilePath = path.join(
        filePath, '../test_sounds/data_sets/', dataSet + '/metadata.json')

    with open(jsonFilePath) as f:
        data = json.load(f)
        tests = []
        validators = []

        for x in data:
            if x.get(split) == SplitEnum.test.value:
                tests.append(EvalObject(x.get(audio_file), x.get(
                    midi_file), SplitEnum.test, data_set_path, x.get(canonical_title)))
            elif x.get(split) == SplitEnum.validation.value:
                validators.append(EvalObject(x.get(audio_file), x.get(
                    midi_file), SplitEnum.validation, data_set_path, x.get(canonical_title)))
    return tests, validators


def create_results_folder(dataSet):
    """
    Tworzenie folderów do przechowywania MIDI wyników transkrypcji
    """
    now = datetime.now()
    formattedNow = now.strftime("%d-%m-%Y_%H-%M-%S")
    filePath = path.dirname(path.abspath(__file__))

    resBaseFolder = path.join(filePath, '../evaluation_results/' + dataSet)
    resFolder = path.join(
        filePath, '../evaluation_results/' + dataSet + '/' + str(formattedNow))
    resFolderTest = path.join(
        filePath, '../evaluation_results/' + dataSet + '/' + str(formattedNow) + '/test/')
    resFolderValidation = path.join(
        filePath, '../evaluation_results/', dataSet + '/' + str(formattedNow) + '/validation/')

    if not os.path.isdir(resBaseFolder):
        os.mkdir(resBaseFolder)
    if not os.path.isdir(resFolder):
        os.mkdir(resFolder)
    if not os.path.isdir(resFolderTest):
        os.mkdir(resFolderTest)
    if not os.path.isdir(resFolderValidation):
        os.mkdir(resFolderValidation)
    return resFolder, resFolderTest, resFolderValidation


def run_transcription(func, isResMidi, normalizedData, sample_rate, neighbourMerging, frameWidth, spacing, *restArgs):
    if isResMidi:
        resMidi, *_ = func(normalizedData, sample_rate,
                           neighbourMerging, frameWidth, spacing, *restArgs)
    else:
        best_frequencies, * \
            _ = func(normalizedData, sample_rate,
                     frameWidth, spacing, *restArgs)
        resMidi, _ = res_in_hz_to_midi_notes(
            best_frequencies, sample_rate, spacing, neighbourMerging)

    return resMidi


def validate_all_arguments(func, args, evalObjects, saveRes, isResMidi=False):
    possible_args_combinations = list(product(*list(args.values())))
    print("Validating " + str(len(possible_args_combinations)) +
          " possible arguments for function " + str(func.__name__))

    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        processes = []
        best_f1 = 0
        best_args = None
        idx = 1
        for arg in possible_args_combinations:
            processes.append(executor.submit(validate_arguments, func, arg, evalObjects,
                                             saveRes, isResMidi, False, str(idx) + "/" + str(len(possible_args_combinations))))
            idx += 1
        for res in processes:
            curr_arg, curr_f1 = res.result()
            if curr_f1 > best_f1:
                best_f1 = curr_f1
                best_args = curr_arg
            print(func.__name__, curr_arg, curr_f1)
        text_file = open(saveRes + "Results_" + func.__name__ + ".txt", "w")
        print(func.__name__ + "\nbest arguments: " +
              str(best_args) + "\nbest F1: " + str(best_f1))
        text_file.writelines(func.__name__ + "\nbest arguments: " +
                             str(best_args) + "\nbest F1: " + str(best_f1) + "\n")
        text_file.close()
        executor.shutdown()
    return best_args, best_f1


def validate_arguments(func, currArgs, evalObjects, saveRes, isResMidi=False, shouldSave=False, debugMessage=""):
    currF1 = 0
    print("Iteration: " + debugMessage)
    for evObj in evalObjects:
        saveDist = (saveRes + evObj.audio_name + "_" + func.__name__ + "_" +
                    str(currArgs) + ".mid").replace(", ", "_").replace("(", "").replace(")", "")
        _, _, _, F1, _, _, _ = evObj.test_method(lambda normalizedData, sample_rate: run_transcription(
            func, isResMidi, normalizedData, sample_rate, *currArgs), max_error=max_error, save_dist=saveDist if shouldSave else None)
        currF1 += F1
    currF1 /= len(evalObjects)
    print(debugMessage + " for arguments " +
          str(currArgs) + " result F1: " + str(currF1))

    return currArgs, currF1


def run_all_tests_on_method(func, arg, evalObjects, saveRes):
    FN, FP, TP, F1, percision, recall, accuracy, processes = [], [], [], [], [], [], [], []
    print("Testing function " + str(func.__name__))
    if arg is None:
        print("Testing function " + str(func.__name__) + " failed - arg is None")
        return F1Results(0, 0, 0, 0, 0, 0, 0, func.__name__)
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        for evalObj in evalObjects:
            processes.append(executor.submit(
                run_test_on_method, func, arg, evalObj, saveRes))
        for res in processes:
            currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy, profileData = res.result()
            FN.append(currFN)
            FP.append(currFP)
            TP.append(currTP)
            F1.append(currF1)
            percision.append(currPercision)
            recall.append(currRecall)
            accuracy.append(currAccuracy)
            update_prof_data(func.__name__, profileData)
            print(func.__name__, currFN, currFP, currTP, currF1,
                  currPercision, currRecall, currAccuracy, profileData)
        executor.shutdown()

    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, func.__name__)


def run_test_on_method(func, arg, evalObj, saveRes):
    currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = evalObj.test_method(lambda normalizedData, sample_rate: func(normalizedData, sample_rate, *arg),
                                                                                                  max_error=max_error, save_dist=(saveRes + evalObj.audio_name + "_" + func.__name__ + "_" + str(arg) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))
    return currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy, get_and_clear_prof_data(func.__name__)


def test_method_onsets(onsets, evalObjects, saveRes):
    FN, FP, TP, F1, percision, recall, accuracy, processes = [], [], [], [], [], [], [], []
    print("Testing function Onsets and Frames")

    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        for evalObj in evalObjects:
            currFile = open(evalObj.get_audio_path(), 'rb')
            uploaded = {
                str(currFile.name): currFile.read()
            }
            sample_rate, normalizedData = loadNormalizedSoundFile(
                evalObj.get_audio_path())
            resp_file_path = saveRes + (evalObj.audio_name + "_" + run_onsets_and_frames.__name__ +
                                        "_" + "Maestro2.0Args" + ".mid").replace(", ", "_").replace("(", "").replace(")", "")
            processes.append(executor.submit(run_onsets_and_frames_wrap, normalizedData, sample_rate,
                                             onsets, uploaded, resp_file_path, load_midi_file(evalObj.get_midi_path())))

        for res in processes:
            currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy, profileData = res.result()
            FN.append(currFN)
            FP.append(currFP)
            TP.append(currTP)
            F1.append(currF1)
            percision.append(currPercision)
            recall.append(currRecall)
            accuracy.append(currAccuracy)
            update_prof_data("run_onsets_and_frames", profileData)
            print("run_onsets_and_frames", currFN, currFP, currTP, currF1,
                  currPercision, currRecall, currAccuracy, profileData)
        executor.shutdown()

    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, "run_onsets_and_frames")


def test_method_gpu(func, arg, evalObjects, saveRes, thr):
    FN, FP, TP, F1, percision, recall, accuracy = [], [], [], [], [], [], []
    print("Testing function " + str(func.__name__))

    def run_fun(normalizedData, sample_rate):
        resMidi = func(normalizedData, sample_rate, thr, *arg)
        return resMidi

    for evObj in evalObjects:
        currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = evObj.test_method(lambda normalizedData, sample_rate: run_fun(
            normalizedData, sample_rate), max_error=max_error, save_dist=(saveRes + evObj.audio_name + "_" + func.__name__ + "_" + str(arg) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))
        FN.append(currFN)
        FP.append(currFP)
        TP.append(currTP)
        F1.append(currF1)
        percision.append(currPercision)
        recall.append(currRecall)
        accuracy.append(currAccuracy)

    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, func.__name__)


## Opakowania metod transkrypcji. Ma to na celu ujednoliczenie sposobu wywoływania
## algorytmów oraz wyodrębnienie części, na której zliczany jest czas
# region Opakowania metod transkrypcji
@profile
def run_ac(normalizedData, sample_rate, neighbourMerging, frameWidth, spacing, fqMin, fqMax):
    best_frequencies, * \
        _ = autocorrelation(normalizedData, sample_rate,
                            frameWidth, spacing, fqMin, fqMax)
    resMidi, _ = res_in_hz_to_midi_notes(
        best_frequencies, sample_rate, spacing, neighbourMerging)
    return resMidi


@profile
def run_aclos(normalizedData, sample_rate, neighbourMerging, frameWidth, spacing, *restArgs):
    best_frequencies, *_ = aclos(normalizedData,
                                 sample_rate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(
        best_frequencies, sample_rate, spacing, neighbourMerging)
    return resMidi


@profile
def run_ceps(normalizedData, sample_rate, neighbourMerging, frameWidth, spacing, *restArgs):
    best_frequencies, * \
        _ = cepstrum_f0_analysis(
            normalizedData, sample_rate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(
        best_frequencies, sample_rate, spacing, neighbourMerging)
    return resMidi


@profile
def run_ceps_gpu(normalizedData, sample_rate, thr, neighbourMerging, frameWidth, spacing, *restArgs):
    _, best_frequencies, _ = cepstrum_f0_analysis_gpu(
        thr, None, normalizedData, sample_rate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(
        best_frequencies, sample_rate, spacing, neighbourMerging)
    return resMidi


@profile
def run_generative_method_2008(normalizedData, sample_rate, *restArgs):
    resMidi, * \
        _ = harmonic_and_smoothness_based_transcription(
            normalizedData, sample_rate, *restArgs)
    return resMidi


@profile
def run_generative_method_2012(normalizedData, sample_rate, *restArgs):
    resMidi, * \
        _ = harmonic_and_smoothness_based_transcription(
            normalizedData, sample_rate, *restArgs)
    return resMidi


def run_onsets_and_frames_wrap(normalizedData, sample_rate, onsets, uploaded, responseFilePath, gtNotes):
    currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = run_onsets_and_frames(
        normalizedData, sample_rate, onsets, uploaded, responseFilePath, gtNotes)
    return currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy, get_and_clear_prof_data("run_onsets_and_frames")


@profile
def run_onsets_and_frames(normalizedData, sample_rate, onsets, uploaded, responseFilePath, gtNotes):
    """
    argumenty normalizedData i sample_rate potrzebne do @profile
    """
    onsets.transcribe(uploaded, responseFilePath)
    evalNotes = load_midi_file(responseFilePath)
    return compare_midi_to_ground_truth(evalNotes, gtNotes, max_error)
# endregion Opakowania metod transkrypcji


def run_test_on_dataset_with_args(tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args, iterations=10, onlyPoli=False):
    """
    Metoda wykonująca testy na wszystkich algorytmach z zadanymi parametrami
    """
    #region initializacja
    onsets = OnsetsAndFramesImpl()
    ## initializacja karty graficznej
    pycuda.driver.init()  # pylint: disable=no-member
    dev = pycuda.driver.Device(0)  # pylint: disable=no-member
    ctx = dev.make_context()
    api = cuda_api()
    thr = api.Thread.create()
    #endregion initializacja

    #region testowanie algorytmów
    for idx in range(0, iterations):
        print("Test iteration: %d/%d" % (idx+1, iterations))
        if not onlyPoli:
            acResults = run_all_tests_on_method(
                run_ac, bestAcArgs, tests, resFolderTest)
            aclosResults = run_all_tests_on_method(
                run_aclos, bestAclosArgs, tests, resFolderTest)
            cepsResults = run_all_tests_on_method(
                run_ceps, bestCepstrumArgs, tests, resFolderTest)
            # Jedyna metoda która nie wykonuje się w podprocesach żeby nie zakłócać GPU
            cepsGpuResults = test_method_gpu(
                run_ceps_gpu, bestCepstrumArgs, tests, resFolderTest, thr)

        generative2008Results = run_all_tests_on_method(
            run_generative_method_2008, bestGenerativeMethodByPertusaAndInesta2008Args, tests, resFolderTest)
        generative2012Results = run_all_tests_on_method(
            run_generative_method_2012, bestGenerativeMethodByPertusaAndInesta2012Args, tests, resFolderTest)
        onsetsResults = test_method_onsets(onsets, tests, resFolderTest)
    #endregion testowanie algorytmów
    ctx.pop()
    pycuda.tools.clear_context_caches()
    for res in [acResults, aclosResults, cepsResults, cepsGpuResults, generative2008Results, generative2012Results, onsetsResults]:
        resText = res.print_results()
        print(resText)
        text_file = open(resFolder + "Results_all.txt", "a")
        text_file.writelines(resText)
        text_file.close()


def run_evals(validators, resFolderValidation, onlyPoli):
    """
    Metoda wyszukująca najlepsze argumenty dla wszystkich funkcji 
    (lub tylko funkcji Pertusa i Inesta 2008/2012 jeśli argument onlyPoli=True)
    """
    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #region wyznaczenie najlepszych argumentów przez walidacje
    if not onlyPoli:
        bestAcArgs, _ = validate_all_arguments(
            autocorrelation, argsAc, validators, resFolderValidation)
        bestAclosArgs, _ = validate_all_arguments(
            aclos, argsAclos, validators, resFolderValidation)
        bestCepstrumArgs, _ = validate_all_arguments(
            cepstrum_f0_analysis, argscepstrum_f0_analysis, validators, resFolderValidation)
    bestGenerativeMethodByPertusaAndInesta2008Args, _ = validate_all_arguments(
        harmonic_and_smoothness_based_transcription, argsGenerativeMethodByPertusaAndInesta2008, validators, resFolderValidation, isResMidi=True)
    bestGenerativeMethodByPertusaAndInesta2012Args, _ = validate_all_arguments(
        harmonic_and_smoothness_based_transcription, argsGenerativeMethodByPertusaAndInesta2012, validators, resFolderValidation, isResMidi=True)
    #endregion wyznaczenie najlepszych argumentów przez walidacje
    return bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args


def run_eval_and_test_on_dataset(dataSet, iterations=10, onlyPoli=False):
    """
    Wyliczenie najlepszych argumentów funkcji i wykonanie przy
    ich pomocy testów wszystkich algorytmów
    (lub tylko funkcji Pertusa i Inesta 2008/2012 jeśli argument onlyPoli=True)
    """
    #region initializacja
    tests, validators = load_metadata(dataSet)
    resFolder, resFolderTest, resFolderValidation = create_results_folder(
        dataSet)
    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #endregion initializacja

    #region wyznaczenie najlepszych argumentów przez walidacje
    bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args = run_evals(
        validators, resFolderValidation, onlyPoli)

    run_test_on_dataset_with_args(tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs,
                                  bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args, iterations=iterations, onlyPoli=onlyPoli)


def run_test_with_predefined_args_on_dataset(dataSet):
    """
    Wykonanie testów wszystkich algorytmów przy pomocy
    wcześniej wyliczoncyh najlepszych argumentów (zmienne best_arg_*)
    (lub tylko funkcji Pertusa i Inesta 2008/2012 i Onsets And Frames jeśli argument onlyPoli=True)
    """
    #region initializacja
    tests, _ = load_metadata(dataSet)
    resFolder, resFolderTest, _ = create_results_folder(
        dataSet)
    #endregion initializacja
    run_test_on_dataset_with_args(tests, resFolder, resFolderTest, best_arg_ac,
                                  best_arg_aclos, best_arg_ceps, best_arg_Generative2008, best_arg_Generative2012)


def get_part_of_test_dataset(dataset, quantity_of_data_to_take):
    """
    Wylosowanie części zbioru danych do testów
    Args:
        dataset: nazwa zbioru danych,
        quantity_of_data_to_take: ilość przypadków testowych do wylosowania
    """
    tests, _ = load_metadata(dataset)
    res = []
    if quantity_of_data_to_take > len(tests):
        raise Exception("Dataset smaller then quantity_of_data_to_take (" +
                        str(quantity_of_data_to_take) + "/" + str(len(tests)) + ").")
    while True:
        for test in tests:
            if uniform(0, 1) > 0.5 and test not in res:
                res.append(test)
            if len(res) == quantity_of_data_to_take:
                return res


def get_part_of_eval_dataset(dataSet, quantity_of_data_to_take):
    """
    Wylosowanie części zbioru danych do ewaluacji najlepszych argumentów
    Params:
        dataset: nazwa zbioru danych,
        quantity_of_data_to_take: ilość przypadków testowych do wylosowania
    """
    _, evals = load_metadata(dataSet)
    res = []
    if quantity_of_data_to_take > len(evals):
        raise Exception("Dataset smaller then quantity_of_data_to_take (" +
                        str(quantity_of_data_to_take) + "/" + str(len(evals)) + ").")
    while True:
        for currEval in evals:
            if uniform(0, 1) > 0.5 and currEval not in res:
                res.append(currEval)
            if len(res) == quantity_of_data_to_take:
                return res


def run_eval_and_test_on_part_of_dataset(dataSet, quantity_evals=1, quantity_tests=2, iterations=1, onlyPoli=False):
    """
    Wyliczenie najlepszych argumentów funkcji i wykonanie przy
    ich pomocy testów wszystkich algorytmów
    (lub tylko funkcji Pertusa i Inesta 2008/2012 jeśli argument onlyPoli=True)
    z wylosowanego wycinka danych
    Params:
        dataSet: nazwa zbioru danych,
        quantity_evals: ilość przypadków testowych do wylosowania dla wyznaczenia argumentów
        quantity_tests: ilość przypadków testowych do wylosowania dla testów
        iterations: ilość iteracji testów (do znormalizowania czasu)
        onlyPoli: czy wykonać tylko algorytmy przeznaczone dla sygnałów polifonicznych

    """
    #region initializacja
    validators = get_part_of_eval_dataset(dataSet, quantity_evals)
    tests = get_part_of_test_dataset(dataSet, quantity_tests)

    print("Selected validators: ")
    for validator in validators:
        print(validator.audio_name)
    print("Selected tests: ")
    for test in tests:
        print(test.audio_name)

    resFolder, resFolderTest, resFolderValidation = create_results_folder(
        dataSet)
    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #endregion initializacja

    #region wyznaczenie najlepszych argumentów przez walidacje
    bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args = run_evals(
        validators, resFolderValidation, onlyPoli)
    run_test_on_dataset_with_args(tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs,
                                  bestGenerativeMethodByPertusaAndInesta2008Args, bestGenerativeMethodByPertusaAndInesta2012Args, iterations=iterations, onlyPoli=onlyPoli)
    #endregion wyznaczenie najlepszych argumentów przez walidacje


if __name__ == "__main__":
    run_eval_and_test_on_part_of_dataset("monoSound")
