import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from utils.plots import plot_pitches, plot_correlogram, plot_wave
from utils.general import loadNormalizedSoundFIle
import numpy as np
from tqdm import tqdm
import sys
from os import path
from math import ceil, floor
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from io import BytesIO


# autocorrelation function on the waveform
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

  for i in tqdm(range(0, ceil((len(data)-frameWidth)/spacing))):
    frame = data[i*spacing:i*spacing+frameWidth] * hann
    res = ac(frame, minLag, maxLag)
    correlogram.append(res)
    bestLag = np.argmax(res)
    bestFq.append(0 if bestLag < minLag else sampleRate/bestLag)

  return correlogram, bestFq


def autocorrelationWrap(filePath, resPath):
  fqMin = 50
  fqMax = 2000
  frameWidth = 2048
  spacing = 2048
  sampleRate, data = loadNormalizedSoundFIle(filePath)
  correlogram, best_frequencies = autocorrelation(
      data, frameWidth, sampleRate, frameWidth, fqMin, fqMax)
  fig, _ = plot_pitches(best_frequencies, spacing, sampleRate, show=False)
  fig2, _ = plot_correlogram(correlogram, spacing, sampleRate, show=False)
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

    sampleRate, data = loadNormalizedSoundFIle(filePath)

    correlogram, best_frequencies = autocorrelation(
        data, frameWidth, sampleRate, frameWidth, fqMin, fqMax)

    print(sampleRate)

    plot_pitches(best_frequencies, spacing, sampleRate)
    plot_correlogram(correlogram, spacing, sampleRate)
    plot_wave(data, sampleRate, "are FE", "eng")