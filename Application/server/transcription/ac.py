import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from utils.plots import plot_pitches, plot_correlogram, plot_wave, plot_correlation
from utils.general import loadNormalizedSoundFIle
import numpy as np
from tqdm import tqdm
import sys
from os import path
from math import ceil, floor
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from io import BytesIO
from utils.midi import res_in_hz_to_midi_notes, write_midi, load_midi_file

# Funkcja autokorelacji operująca na sygnale audio w domenie czasu
def autocorrelation(data, frameWidth, sampleRate, spacing, fqMin, fqMax):
  def ac(data, minLag, maxLag):
    result = list(np.zeros(minLag))
    n = len(data)
    for lag in range(minLag, maxLag):
        sumarray = np.zeros(n+lag)
        sumarray[:n] = data
        sumarray[:n-lag] *= data[lag:]
        sum = np.sum(sumarray[:n-lag])
        result.append(float(sum/(n-lag)))
    return result

  bestFq = []
  correlogram = []
  hann = np.hanning(frameWidth)
  minLag = int(floor(sampleRate / fqMax))
  maxLag = int(ceil(sampleRate / fqMin))

  for i in tqdm(range(0, int(ceil((len(data) - frameWidth) / spacing)))):
    frame = data[i*spacing:i*spacing+frameWidth] * hann
    res = ac(frame, minLag, maxLag)
    correlogram.append(res)
    bestLag = np.argmax(res)
    bestFq.append(0 if bestLag < minLag else sampleRate/bestLag)

  return correlogram, bestFq

## For client-server usage
def autocorrelation_wrapped(filePath):
  fqMin = 50
  fqMax = 2000
  frameWidth = 2048
  spacing = 2048
  sampleRate, data = loadNormalizedSoundFIle(filePath)
  correlogram, best_frequencies = autocorrelation(
      data, frameWidth, sampleRate, frameWidth, fqMin, fqMax)
  fig, _ = plot_pitches(best_frequencies, spacing, sampleRate, show=False, language="pl")
  fig2, _ = plot_correlogram(correlogram, spacing, sampleRate, show=False, language="pl")
  pitches, correlogram = BytesIO(), BytesIO()
  fig.savefig(pitches, format="png")
  fig2.savefig(correlogram, format="png")
  return pitches, correlogram


if __name__ == "__main__":
    fqMin = 50
    fqMax = 2000
    frameWidth = 2048
    spacing = 2048

    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/ode_to_joy_(9th_symphony)/ode_to_joy_(9th_symphony).wav')
    #filePath = path.join(filePath, '../test_sounds/Chopin_prelude28no.4inEm/chopin_prelude_28_4.wav')
    #filePath = path.join(filePath, '../test_sounds/EmPiano/Em.wav')


    sampleRate, data = loadNormalizedSoundFIle(filePath)

    correlogram, best_frequencies = autocorrelation(
        data, frameWidth, sampleRate, frameWidth, fqMin, fqMax)

    plot_pitches(best_frequencies, spacing, sampleRate, language="pl")
    #plot_correlogram(correlogram, spacing, sampleRate, language="pl", showColorbar=False)
    #plot_wave(data, sampleRate, "Ode to joy (9th_symphony)", language="pl", x_axis_as_samples=True)

    #plot_correlation(correlogram[10], sampleRate, "pl")
    #x = correlogram[10]
    #xarg = np.argmax(x)
    #x[(xarg-8):(xarg+8)] = np.zeros(16)
    #print(np.argmax(x), xarg)
    resMidi, resPianoRoll = res_in_hz_to_midi_notes(best_frequencies, sampleRate, spacing)
    write_midi(resMidi, "./resAC.mid")

    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../resAC.mid')
    res = load_midi_file(filePath)

    for i in range(0, len(res)):
      res[i].print_self()
      resMidi[i].print_self()
      print(".......................")
    assert len(res) == len(resMidi)