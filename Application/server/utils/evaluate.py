import sys
import os
from datetime import datetime
from os import path
from general import loadNormalizedSoundFIle
from midi import load_midi_file, compare_midi_to_ground_truth, res_in_hz_to_midi_notes, write_midi

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from transcription.ac import autocorrelation
from transcription.aclos import aclos
from transcription.cepstrumF0Analysis import cepstrumF0Analysis, ceostrumF0AnalysisGpu
from transcription.jointMethodByPertusAndInesta import harmonic_and_smoothness_based_transcription
from transcription.onsetsAndFrames import OnsetsAndFramesImpl
import json
import enum
from utils.custom_profile import profile, print_prof_data

from itertools import product

audio_file = "audio_filename"
midi_file = "midi_filename"
split = "split"
canonical_title = "canonical_title"

maxErr = 0.08
stdFrameWidth = [1024, 2048, 4096, 8192]
stdSpacing = [1024, 512]
stdZeroPadding = [1024, 2048, 4096, 8192]
stdMinF0 = [50, 85, 100]
stdMaxF0 = [2000, 5500]

argsAc = {
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'fqMin': stdMinF0,
    'fqMax': stdMaxF0
}

argsAclos = {
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding
}

argsCepstrumF0Analysis = {
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding
}

argsJointMethodByPertusaAndInesta2008 = {
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6, 8],
    'relevantPowerThreashold': [4, 8],
    'maxInharmonyDegree': [0.08, 0.16],
    'minHarmonicsPerCandidate': [2, 3],
    'maxHarmonicsPerCandidate': [6, 10],
    'maxCandidates': [6, 8],
    'maxParallelNotes': [4, 5],
    'gamma': [0.05, 0.1],
    'minNoteMs': [70],
    'useLiftering': [False, True],
    'lifteringCoefficient': [6, 8],
    'minNoteVelocity': [10, 30],
    'newAlgorithmVersion': [False],
    'smoothnessImportance': [None], #TODO: Czy to było dobrze opisane w Thesis?
    'temporalSmoothnessRange': [None],
    'pitch_tracking_combinations': [None]
}

argsJointMethodByPertusaAndInesta2012 = {
    'frameWidth': stdFrameWidth,
    'spacing': stdSpacing,
    'sizeOfZeroPadding': stdZeroPadding,
    'minF0': stdMinF0,
    'maxF0': stdMaxF0,
    'peakDistance': [6, 8],
    'relevantPowerThreashold': [4, 8],
    'maxInharmonyDegree': [0.08, 0.16],
    'minHarmonicsPerCandidate': [2, 3],
    'maxHarmonicsPerCandidate': [6, 10],
    'maxCandidates': [6, 8],
    'maxParallelNotes': [4, 5],
    'gamma': [0.05, 0.1],
    'minNoteMs': [70],
    'useLiftering': [False, True],
    'lifteringCoefficient': [6, 8],
    'minNoteVelocity': [10, 30],
    'newAlgorithmVersion': [False],
    'smoothnessImportance': [3, 6], #TODO: Czy to było dobrze opisane w Thesis?
    'temporalSmoothnessRange': [2, 3],
    'pitch_tracking_combinations': [2, 3]
}

class SplitEnum(enum.Enum):
    test = "test"
    train = "train"
    validation = "validation"

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


def run_transcription(func, isResMidi, normalizedData, sampleRate, frameWidth, spacing, *restArgs):
    if isResMidi:
        resMidi, *_ = func(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    else:
        best_frequencies, *_ = func(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
        resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing)

    return resMidi

def validate_arguments(func, args, evalObjects, saveRes, isResMidi = False):
    possibleCombinations = list(product(*list(args.values())))
    bestF1 = 0
    bestArgs = None
    for currArgs in possibleCombinations:
        currF1 = 0
        print(currArgs)
        for evObj in evalObjects:
            _, _, _, F1, _, _ = evObj.test_method(lambda normalizedData, sampleRate: run_transcription(
                func, isResMidi, normalizedData, sampleRate, *currArgs), maxErr=maxErr, save_dist=(saveRes + evObj.audioName + "_" + func.__name__ + "_" + str(currArgs) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))
            currF1 += F1
        currF1 /= len(evalObjects)
        if currF1 > bestF1:
            bestF1 = currF1
            bestArgs = currArgs
    text_file = open(saveRes + "Results_" + func.__name__  + ".txt" , "w")
    text_file.writelines(func.__name__  + "\nbest arguments: " + str(currArgs) + "\nbest F1: " + str(bestF1) + "\n")
    text_file.close()
    return bestArgs, bestF1
    
def test_method(func, arg, evalObjects, saveRes, isResMidi = False):
    FN, FP, TP, F1, percision, recall = [], [], [], [], [], []
    for evObj in evalObjects:
        currFN, currFP, currTP, currF1, currPercision, currRecall = evObj.test_method(lambda normalizedData, sampleRate: func(
            normalizedData, sampleRate, *arg), maxErr=maxErr, save_dist=(saveRes + evObj.audioName + "_" + func.__name__ + "_" + str(arg) + ".mid").replace(", ", "_").replace("(", "").replace(")", ""))
        FN.append(currFN)
        FP.append(currFP)
        TP.append(currTP)
        F1.append(currF1)
        percision.append(currPercision)
        recall.append(currRecall)
    return FN, FP, TP, F1, percision, recall

def test_method_onsets(onsets, evalObjects, saveRes):
    FN, FP, TP, F1, percision, recall = [], [], [], [], [], []
    for evObj in evalObjects:
        currFile = open(evObj.get_audio_path(), 'rb')
        uploaded = {
            str(currFile.name): currFile.read()
        }
        respFilePath = saveRes + (evObj.audioName + "_" + run_onsets_and_frames.__name__ + "_" + "Maestro2.0Args" + ".mid").replace(", ", "_").replace("(", "").replace(")", "")
        run_onsets_and_frames(onsets, uploaded, respFilePath)
        evalNotes = load_midi_file(respFilePath)
        gtNotes = load_midi_file(evObj.get_midi_path())
        
        
        currFN, currFP, currTP, currF1, currPercision, currRecall = compare_midi_to_ground_truth(evalNotes, gtNotes, maxErr)
        write_midi(evalNotes, "./test.mid")
        FN.append(currFN)
        FP.append(currFP)
        TP.append(currTP)
        F1.append(currF1)
        percision.append(currPercision)
        recall.append(currRecall)
    return FN, FP, TP, F1, percision, recall

@profile
def run_ac(normalizedData, sampleRate, frameWidth, spacing, fqMin, fqMax):
    best_frequencies, *_ = autocorrelation(normalizedData, sampleRate, frameWidth, spacing, fqMin, fqMax)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing)
    return resMidi

@profile
def run_aclos(normalizedData, sampleRate, frameWidth, spacing, *restArgs):
    best_frequencies, *_ = aclos(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing)
    return resMidi

@profile
def run_ceps(normalizedData, sampleRate, frameWidth, spacing, *restArgs):
    best_frequencies, *_ = cepstrumF0Analysis(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    resMidi, _ = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing)
    return resMidi

@profile
def run_joint_method_2008(normalizedData, sampleRate, frameWidth, spacing, *restArgs):
    resMidi, *_ = harmonic_and_smoothness_based_transcription(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    return resMidi

@profile
def run_joint_method_2012(normalizedData, sampleRate, frameWidth, spacing, *restArgs):
    resMidi, *_ = harmonic_and_smoothness_based_transcription(normalizedData, sampleRate, frameWidth, spacing, *restArgs)
    return resMidi

@profile
def run_onsets_and_frames(onsets, uploaded, responseFilePath):
    onsets.transcribe(uploaded, responseFilePath)
    return 


def run_eval_and_test_on_dataset(dataSet):
    #region initializacja
    tests, validators = load_metadata(dataSet)
    resFolder, resFolderTest, resFolderValidation = create_results_folder(
        dataSet)
    onsets = OnsetsAndFramesImpl()
    #endregion initializacja
    #region wyznaczenie najlepszych argumentów przez walidacje
    bestAcArgs = validate_arguments(
        autocorrelation, argsAc, tests, resFolderValidation)
    bestAclosArgs = validate_arguments(
        aclos, argsAclos, tests, resFolderValidation)
    bestCepstrumArgs = validate_arguments(
        cepstrumF0Analysis, argsCepstrumF0Analysis, tests, resFolderValidation)
    bestJointMethodByPertusaAndInesta2008Args = validate_arguments(
        harmonic_and_smoothness_based_transcription, argsJointMethodByPertusaAndInesta2008, tests, resFolderValidation, True)
    bestJointMethodByPertusaAndInesta2012Args = validate_arguments(
        harmonic_and_smoothness_based_transcription, argsJointMethodByPertusaAndInesta2012, tests, resFolderValidation, True)
    #endregion wyznaczenie najlepszych argumentów przez walidacje
    

    FN, FP, TP, F1, percision, recall = test_method_onsets(onsets, tests, resFolderTest) ##TODO: Miary statystyczne do jakiejś klasy
    print(F1)

    


if __name__ == "__main__":
    #region transcription initialization Onsets and Frames
    #onsets = OnsetsAndFramesImpl()
    # onsets.initializeModel()
    #tests, validators = load_metadata("monoSound")
    run_eval_and_test_on_dataset("monoSound")
    #tests[0].test_method(test_ac, 0.1)