from utils.plots import plot_pitches, plot_correlogram
from utils.general import loadNormalizedSoundFIle
import numpy as np
from tqdm import tqdm
import sys
from os import path
from math import ceil, floor
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


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
  fqMaxx = 2000
  frameWidth = 2048
  spacing = 2048
  sampleRate, data = loadNormalizedSoundFIle(filePath)
  correlogram, best_frequencies = autocorrelation(
      data, frameWidth, sampleRate, frameWidth, fqMin, fqMaxx)
  fig, ax = plot_pitches(best_frequencies, spacing, sampleRate, show=False)
  fig.savefig(resPath)
  #fig, ax = plot_correlogram(correlogram, spacing, sampleRate, show=False)
  #fig.savefig(path.join(resPath, 'correlogram.png'))


if __name__ == "__main__":
    fqMin = 50
    fqMaxx = 2000
    frameWidth = 2048
    spacing = 2048

    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)

    correlogram, best_frequencies = autocorrelation(
        data, frameWidth, sampleRate, frameWidth, fqMin, fqMaxx)

    plot_pitches(best_frequencies, spacing, sampleRate)
    plot_correlogram(correlogram, spacing, sampleRate)
