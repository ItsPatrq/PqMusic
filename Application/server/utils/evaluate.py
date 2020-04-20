import sys
import os
from datetime import datetime
from os import path
from general import loadNormalizedSoundFIle
from midi import load_midi_file, compare_midi_to_ground_truth, res_in_hz_to_midi_notes, write_midi
from random import uniform
import concurrent.futures
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from transcription.ac import autocorrelation
from transcription.aclos import aclos
from transcription.cepstrumF0Analysis import cepstrumF0Analysis
from transcription.cepstrumF0AnalysisGpu import cepstrumF0AnalysisGpu
from transcription.jointMethodByPertusAndInesta import harmonic_and_smoothness_based_transcription
from transcription.onsetsAndFrames import OnsetsAndFramesImpl
import json
import enum
from utils.custom_profile import profile, print_normalize_profile_data
from pycuda import cumath
import pycuda.driver
from itertools import product
from reikna.cluda import cuda_api
audio_file = "audio_filename"
midi_file = "midi_filename"
split = "split"
canonical_title = "canonical_title"

maxErr = 0.085

stdFrameWidth = [2048]
stdSpacing = [512]
stdZeroPadding = [12288]
stdMinF0 = [50]
stdMaxF0 = [5500]
stdNeighbourMerging = [3]

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

argsCepstrumF0Analysis = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding
}

argsJointMethodByPertusaAndInesta2008 = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6,8],
    'relevantPowerThreashold': [4, 2],
    'maxInharmonyDegree': [0.22, 0.32],
    'minHarmonicsPerCandidate': [1, 2],
    'maxHarmonicsPerCandidate': [8],
    'maxCandidates': [6],
    'maxParallelNotes': [7],
    'gamma': [0.1, 0.08],
    'minNoteMs': [55.68],
    'lifteringCoefficient': [0, 6],
    'minNoteVelocity': [16],
    'newAlgorithmVersion': [False],
    'smoothnessImportance': [None], #TODO: Czy to było dobrze opisane w Thesis?
    'temporalSmoothnessRange': [None],
    'pitch_tracking_combinations': [None]
}

argsJointMethodByPertusaAndInesta2012 = {
    "neighbourMerging": stdNeighbourMerging,
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6, 8],
    'relevantPowerThreashold': [4, 2],
    'maxInharmonyDegree': [0.22],
    'minHarmonicsPerCandidate': [1], #if 2 -> try 3
    'maxHarmonicsPerCandidate': [8],
    'maxCandidates': [7],
    'maxParallelNotes': [7],
    'gamma': [0.1, 0.08],
    'minNoteMs': [70],
    'lifteringCoefficient': [6, 8], #next , 6, 8
    'minNoteVelocity': [15],
    'newAlgorithmVersion': [True],
    'smoothnessImportance': [3, 2], #TODO: Czy to było dobrze opisane w Thesis?
    'temporalSmoothnessRange': [2, 3],
    'pitch_tracking_combinations': [3, 4]
}

best_arg_ac = (1, 1024, 1024, 50, 5500)
best_arg_aclos =  (3, 4096, 1024, 2048)
best_arg_ceps = (3, 4096, 1024, 8192)
best_arg_joint2008 = (3, 2048, 512, 8192, 50, 5500, 8, 2, 0.32, 1, 8, 6, 1, 0.1, 70, 0, 16, False, None, None, None)
best_arg_joint2012 = (3, 2048, 512, 12288, 50, 5500, 8, 4, 0.22, 1, 8, 7, 1, 0.1, 70, 8, 15, True, 3, 2, 4)

class SplitEnum(enum.Enum):
    test = "test"
    train = "train"
    validation = "validation"

class F1Results:
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
            "\nTime estimation: " + print_normalize_profile_data(0, self.algorithm)


class EvalObject:
    def __init__(self, audioFile, midiFile, split, dataSetPath, audioName):
        self.audio = audioFile
        self.midi = midiFile
        self.split = split
        self.dataSetPath = dataSetPath
        self.audioName = audioName

    def test_method(self, method, maxErr, save_dist = None):
        gtNotes = load_midi_file(self.get_midi_path())
        sampleRate, normalizedData = loadNormalizedSoundFIle(self.get_audio_path())
        evalNotes = method(normalizedData, sampleRate)
        if save_dist != None:
            write_midi(evalNotes, save_dist)
        return compare_midi_to_ground_truth(evalNotes, gtNotes, maxErr)

    def get_audio_path(self):
        return path.join(self.dataSetPath, self.audio)

    def get_midi_path(self):
        return path.join(self.dataSetPath, self.midi)

def load_metadata(dataSet):
    filePath = path.dirname(path.abspath(__file__))
    dataSetPath = path.join(filePath, '../test_sounds/data_sets/', dataSet)
    jsonFilePath = path.join(filePath, '../test_sounds/data_sets/', dataSet + '/metadata.json')

    with open(jsonFilePath) as f:
        data = json.load(f)
        tests = []
        validators = []

        for x in data:
            if x.get(split) == SplitEnum.test.value:
                tests.append(EvalObject(x.get(audio_file), x.get(midi_file), SplitEnum.test, dataSetPath, x.get(canonical_title)))
            elif x.get(split) == SplitEnum.validation.value:
                validators.append(EvalObject(x.get(audio_file), x.get(midi_file), SplitEnum.validation, dataSetPath, x.get(canonical_title)))
    return tests, validators

## tworzenie folderów do przechowywania MIDI wyników transkrypcji
def create_results_folder(dataSet):
    now = datetime.now()
    formattedNow = now.strftime("%d-%m-%Y_%H-%M-%S")
    filePath = path.dirname(path.abspath(__file__))

    resBaseFolder = path.join(filePath, '../evaluation_results/' + dataSet)
    resFolder = path.join(filePath, '../evaluation_results/' + dataSet + '/' + str(formattedNow))
    resFolderTest = path.join(filePath, '../evaluation_results/' + dataSet + '/' + str(formattedNow) + '/test/')
    resFolderValidation = path.join(filePath, '../evaluation_results/', dataSet + '/' +  str(formattedNow) + '/validation/')

    if not os.path.isdir(resBaseFolder):
        os.mkdir(resBaseFolder)
    if not os.path.isdir(resFolder):
        os.mkdir(resFolder)
    if not os.path.isdir(resFolderTest):
        os.mkdir(resFolderTest)
    if not os.path.isdir(resFolderValidation):
        os.mkdir(resFolderValidation)
    return resFolder, resFolderTest, resFolderValidation


def run_transcription(func, isResMidi, normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, *restArgs):
    if isResMidi:
        resMidi, *_ = func(normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, *restArgs)
    else:
        best_frequencies, *_ = func(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
        resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing, neighbourMerging)

    return resMidi

def validate_all_arguments(func, args, evalObjects, saveRes, isResMidi = False):
    possibleArgsCombinations = list(product(*list(args.values())))
    print("Validating " + str(len(possibleArgsCombinations)) +" possible arguments for function " + str(func.__name__))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = []
        bestF1 = 0
        bestArgs = None
        idx = 1
        for arg in possibleArgsCombinations:
            processes.append(executor.submit(validate_arguments, func, arg, evalObjects, saveRes, isResMidi, False, str(idx) + "/" + str(len(possibleArgsCombinations))))
            idx += 1
        for res in processes:
            currArg, currF1 = res.result()
            if currF1 > bestF1:
                bestF1 = currF1
                bestArgs = currArg
        text_file = open(saveRes + "Results_" + func.__name__  + ".txt" , "w")
        print(func.__name__  + "\nbest arguments: " + str(bestArgs) + "\nbest F1: " + str(bestF1))
        text_file.writelines(func.__name__  + "\nbest arguments: " + str(bestArgs) + "\nbest F1: " + str(bestF1) + "\n")
        text_file.close()
    return currArg, bestF1

def validate_arguments(func, currArgs, evalObjects, saveRes, isResMidi = False, shouldSave = False, debugMessage = ""):
    currF1 = 0

    for evObj in evalObjects:
        saveDist = (saveRes + evObj.audioName + "_" + func.__name__ + "_" + str(currArgs) + ".mid").replace(", ", "_").replace("(", "").replace(")", "")
        _, _, _, F1, _, _, _ = evObj.test_method(lambda normalizedData, sampleRate: run_transcription(
            func, isResMidi, normalizedData, sampleRate, *currArgs), maxErr=maxErr, save_dist=saveDist if shouldSave else None)
        currF1 += F1
    currF1 /= len(evalObjects)
    print(debugMessage + " " + str(currArgs) + " F1: " + str(currF1))

    return currArgs, currF1

def run_all_tests_on_method(func, arg, evalObjects, saveRes):
    FN, FP, TP, F1, percision, recall, accuracy, processes = [], [], [], [], [], [], [], []
    print("Testing function " + str(func.__name__))
    if arg is None:
        print("Testing function " + str(func.__name__) + " failed - arg is None")
        return F1Results(0, 0, 0, 0, 0, 0, 0, func.__name__)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for evalObj in evalObjects:
            processes.append(executor.submit(run_test_on_method, func, arg, evalObj, saveRes))
        for res in processes:
            currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = res.result()
            FN.append(currFN)
            FP.append(currFP)
            TP.append(currTP)
            F1.append(currF1)
            percision.append(currPercision)
            recall.append(currRecall)
            accuracy.append(currAccuracy)
    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, func.__name__)

def run_test_on_method(func, arg, evalObj, saveRes):
    return evalObj.test_method(lambda normalizedData, sampleRate: func(normalizedData, sampleRate, *arg),
        maxErr=maxErr, save_dist=(saveRes + evalObj.audioName + "_" + func.__name__ + "_" + str(arg) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))

def test_method_onsets(onsets, evalObjects, saveRes):
    FN, FP, TP, F1, percision, recall, accuracy, processes = [], [], [], [], [], [], [], []
    print("Testing function Onsets and Frames")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for evalObj in evalObjects:
            currFile = open(evalObj.get_audio_path(), 'rb')
            uploaded = {
                str(currFile.name): currFile.read()
            }
            respFilePath = saveRes + (evalObj.audioName + "_" + run_onsets_and_frames.__name__ + "_" + "Maestro2.0Args" + ".mid").replace(", ", "_").replace("(", "").replace(")", "")
            processes.append(executor.submit(run_onsets_and_frames, onsets, uploaded, respFilePath, load_midi_file(evalObj.get_midi_path())))
    
    for res in processes:
        currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = res.result()
        FN.append(currFN)
        FP.append(currFP)
        TP.append(currTP)
        F1.append(currF1)
        percision.append(currPercision)
        recall.append(currRecall)
        accuracy.append(currAccuracy)
    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, "run_onsets_and_frames")

def test_method_gpu(func, arg, evalObjects, saveRes, api, thr):
    FN, FP, TP, F1, percision, recall, accuracy = [], [], [], [], [], [], []
    print("Testing function " + str(func.__name__))
    
    def run_fun(normalizedData, sampleRate):
        resMidi = func(api, thr, normalizedData, sampleRate, *arg)
        return resMidi

    for evObj in evalObjects:
        currFN, currFP, currTP, currF1, currPercision, currRecall, currAccuracy = evObj.test_method(lambda normalizedData, sampleRate: run_fun(
            normalizedData, sampleRate), maxErr=maxErr, save_dist=(saveRes + evObj.audioName + "_" + func.__name__ + "_" + str(arg) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))
        FN.append(currFN)
        FP.append(currFP)
        TP.append(currTP)
        F1.append(currF1)
        percision.append(currPercision)
        recall.append(currRecall)
        accuracy.append(currAccuracy)

    return F1Results(FN, FP, TP, F1, percision, recall, accuracy, func.__name__)

@profile
def run_ac(normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, fqMin, fqMax):
    best_frequencies, *_ = autocorrelation(normalizedData, sampleRate, frameWidth, spacing, fqMin, fqMax)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing, neighbourMerging)
    return resMidi

@profile
def run_aclos(normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, *restArgs):
    best_frequencies, *_ = aclos(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing, neighbourMerging)
    return resMidi

@profile
def run_ceps(normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, *restArgs):
    best_frequencies, *_ = cepstrumF0Analysis(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing, neighbourMerging)
    return resMidi

@profile
def run_ceps_gpu(api, thr, normalizedData, sampleRate, neighbourMerging, frameWidth, spacing, *restArgs):
    _, best_frequencies, _ = cepstrumF0AnalysisGpu(api, thr, None, normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing, neighbourMerging)
    return resMidi

@profile
def run_joint_method_2008(normalizedData, sampleRate, *restArgs):
    resMidi, *_ = harmonic_and_smoothness_based_transcription(normalizedData, sampleRate, *restArgs)
    return resMidi

@profile
def run_joint_method_2012(normalizedData, sampleRate, *restArgs):
    resMidi, *_ = harmonic_and_smoothness_based_transcription(normalizedData, sampleRate,*restArgs)
    return resMidi

@profile
def run_onsets_and_frames(onsets, uploaded, responseFilePath, gtNotes):
    onsets.transcribe(uploaded, responseFilePath)
    evalNotes = load_midi_file(responseFilePath)
    return compare_midi_to_ground_truth(evalNotes, gtNotes, maxErr)


def run_test_on_dataset_with_args(dataSet, tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args, iterations = 10, onlyPoli = False):
    #region initializacja
    onsets = OnsetsAndFramesImpl()
    ## initializacja karty graficznej
    pycuda.driver.init() # pylint: disable=no-member
    dev = pycuda.driver.Device(0) # pylint: disable=no-member
    ctx = dev.make_context()
    api = cuda_api()
    thr = api.Thread.create()
    #endregion initializacja

    #region testowanie algorytmów
    for _ in range(0, iterations):
        if not onlyPoli:
            acResults = run_all_tests_on_method(run_ac, bestAcArgs, tests, resFolderTest)
            aclosResults = run_all_tests_on_method(run_aclos, bestAclosArgs, tests, resFolderTest)
            cepsResults = run_all_tests_on_method(run_ceps, bestCepstrumArgs, tests, resFolderTest) 
            cepsGpuResults = test_method_gpu(run_ceps_gpu, bestCepstrumArgs, tests, resFolderTest, api, thr) # Jedyna metoda która nie wykonuje się w podprocesach żeby nie zakłócać GPU
            ctx.pop()
            pycuda.tools.clear_context_caches()
        joint2008Results = run_all_tests_on_method(run_joint_method_2008, bestJointMethodByPertusaAndInesta2008Args, tests, resFolderTest)
        joint2012Results = run_all_tests_on_method(run_joint_method_2012, bestJointMethodByPertusaAndInesta2012Args, tests, resFolderTest)
        onsetsResults = test_method_onsets(onsets, tests, resFolderTest)
    #endregion testowanie algorytmów

    for res in [acResults, aclosResults, cepsResults, cepsGpuResults, joint2008Results, joint2012Results, onsetsResults]:
        resText = res.print_results()
        print(resText)
        text_file = open(resFolder + "Results_all.txt" , "a")
        text_file.writelines(resText)
        text_file.close()

def run_evals(validators, resFolderValidation, onlyPoli):

    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #region wyznaczenie najlepszych argumentów przez walidacje
    if not onlyPoli:
        bestAcArgs, _ = validate_all_arguments(
            autocorrelation, argsAc, validators, resFolderValidation)
        bestAclosArgs, _ = validate_all_arguments(
            aclos, argsAclos, validators, resFolderValidation)
        bestCepstrumArgs, _ = validate_all_arguments(
            cepstrumF0Analysis, argsCepstrumF0Analysis, validators, resFolderValidation)
    bestJointMethodByPertusaAndInesta2008Args, _ = validate_all_arguments(
        harmonic_and_smoothness_based_transcription, argsJointMethodByPertusaAndInesta2008, validators, resFolderValidation, isResMidi=True)
    bestJointMethodByPertusaAndInesta2012Args, _ = validate_all_arguments(
        harmonic_and_smoothness_based_transcription, argsJointMethodByPertusaAndInesta2012, validators, resFolderValidation, isResMidi=True)
    #endregion wyznaczenie najlepszych argumentów przez walidacje
    return bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args


def run_eval_and_test_on_dataset(dataSet, iterations = 10, onlyPoli = False):
    #region initializacja
    tests, validators = load_metadata(dataSet)
    resFolder, resFolderTest, resFolderValidation = create_results_folder(
        dataSet)
    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #endregion initializacja

    #region wyznaczenie najlepszych argumentów przez walidacje
    bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args = run_evals(validators, resFolderValidation, onlyPoli)
    
    run_test_on_dataset_with_args(dataSet, tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args, iterations=iterations, onlyPoli=onlyPoli)


def run_test_with_predefined_args_on_dataset(dataSet):
    #region initializacja
    tests, _ = load_metadata(dataSet)
    resFolder, resFolderTest, _ = create_results_folder(
        dataSet)
    #endregion initializacja
    run_test_on_dataset_with_args(dataSet, tests, resFolder, resFolderTest, best_arg_ac, best_arg_aclos, best_arg_ceps, best_arg_joint2008, best_arg_joint2012)

def get_part_of_test_dataset(dataset, quantityOfDataToTake):
    tests, _ = load_metadata(dataset)
    res = []
    if quantityOfDataToTake > len(tests):
        raise Exception("Dataset smaller then quantityOfDataToTake (" + str(quantityOfDataToTake) + "/" + str(len(tests)) + ").")
    while True:
        for test in tests:
            if uniform(0, 1) > 0.5 and test not in res:
                res.append(test)
            if len(res) == quantityOfDataToTake:
                return res

def get_part_of_eval_dataset(dataSet, quantityOfDataToTake):
    _, evals = load_metadata(dataSet)
    res = []
    if quantityOfDataToTake > len(evals):
        raise Exception("Dataset smaller then quantityOfDataToTake (" + str(quantityOfDataToTake) + "/" + str(len(evals)) + ").")
    while True:
        for currEval in evals:
            if uniform(0, 1) > 0.5 and currEval not in res:
                res.append(currEval)
            if len(res) == quantityOfDataToTake:
                return res

def run_eval_and_test_on_part_of_dataset(dataSet, quantityEvals = 1, quantityTests = 100, iterations = 1, onlyPoli = False):
    #region initializacja
    validators = get_part_of_eval_dataset(dataSet, quantityEvals)
    tests = get_part_of_test_dataset(dataSet, quantityTests)

    print("Selected validators: ")
    for validator in validators:
        print(validator.audioName)
    print("Selected tests: ")
    for test in tests:
        print(test.audioName)
        
    resFolder, resFolderTest, resFolderValidation = create_results_folder(
        dataSet)
    bestAcArgs, bestAclosArgs, bestCepstrumArgs = (), (), ()
    #endregion initializacja

    #region wyznaczenie najlepszych argumentów przez walidacje
    bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args = run_evals(validators, resFolderValidation, onlyPoli)
    run_test_on_dataset_with_args(dataSet, tests, resFolder, resFolderTest, bestAcArgs, bestAclosArgs, bestCepstrumArgs, bestJointMethodByPertusaAndInesta2008Args, bestJointMethodByPertusaAndInesta2012Args, iterations=iterations, onlyPoli=onlyPoli)


def temporary():
    tests, validators = load_metadata("monoSound")
    resFolder, resFolderTest, resFolderValidation = create_results_folder("monoSound")
    
    #bestJointMethodByPertusaAndInesta2012Args, _ = validate_all_arguments(
    #    harmonic_and_smoothness_based_transcription, argsJointMethodByPertusaAndInesta2012, validators, resFolderValidation, isResMidi=True)
    print("POLI")
    run_eval_and_test_on_part_of_dataset("maestro", onlyPoli=True)


if __name__ == "__main__":
    temporary()
