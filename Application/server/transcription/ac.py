import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from utils.plots import plot_pitches, plot_correlogram, plot_wave, plot_correlation
from utils.general import loadNormalizedSoundFile
import numpy as np
from tqdm import tqdm
import sys
from os import path
from math import ceil, floor
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from io import BytesIO
from utils.midi import res_in_hz_to_midi_notes, write_midi, load_midi_file

# Funkcja autokorelacji operująca na sygnale audio w domenie czasu
def autocorrelation(data, sampleRate, frameWidth, spacing, fqMin, fqMax, disableTqdm = True):
  def ac(currFrame, minLag, maxLag):
    res = list(np.zeros(minLag))
    n = len(currFrame)
    for lag in range(minLag, maxLag):
        acRes = np.zeros(n+lag)
        acRes[:n] = currFrame
        acRes[:n-lag] *= currFrame[lag:]
        acSum = np.sum(acRes[:n-lag])
        res.append(acSum/(n-lag))
    return res

  bestFq = []
  correlogram = []
  hann = np.hanning(frameWidth)
  minLag = int(floor(sampleRate / fqMax))
  maxLag = int(ceil(sampleRate / fqMin))

  for i in tqdm(range(0, int(ceil((len(data) - frameWidth) / spacing))), disable=disableTqdm):
    frame = data[i*spacing:i*spacing+frameWidth] * hann
    res = ac(frame, minLag, maxLag)
    correlogram.append(res)
    bestLag = np.argmax(res)
    bestFq.append(0 if bestLag < minLag else sampleRate/bestLag)

  return bestFq, correlogram

## Funkcja do użytku serwera
def autocorrelation_wrapped(filePath):
  fqMin = 50
  fqMax = 2000
  frameWidth = 2048
  spacing = 2048
  sampleRate, data = loadNormalizedSoundFile(filePath)
  best_frequencies, correlogram = autocorrelation(
      data, sampleRate, frameWidth, frameWidth, fqMin, fqMax)
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


    sampleRate, data = loadNormalizedSoundFile(filePath)

    best_frequencies, correlogram = autocorrelation(
        data, sampleRate, frameWidth, frameWidth, fqMin, fqMax)

    plot_pitches(best_frequencies, spacing, sampleRate, language="pl")

