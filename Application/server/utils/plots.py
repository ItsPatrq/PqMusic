from pydub import AudioSegment
import ntpath
import numpy as np
import matplotlib.pyplot as plt
import math
from .general import hz_to_fourier, fourier_to_hz, hz_to_fft
import pylab

defaultFqTicks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
defaultFqTickLabels = [20, 50, 100, 200, 500, '1k', '2k', '5k', '10k', '20k']

def getTimeTicks(spacing, sampleRate, secLength):
  ticks = [0]
  fullSecs = int(math.floor(secLength))  

  for t in np.arange(1, fullSecs + 1):
    ticks.append(t*sampleRate/spacing)
  ticks.append(int(secLength*sampleRate/spacing) - 1)
  
  return ticks

def getTimeTickLabels(secLength):
  fullSecs = int(math.floor(secLength))
  tickLabels = list(np.concatenate(([0], np.arange(1, fullSecs + 1), [round(secLength, 3)])))
  return tickLabels

def getFqTicks(sampleRate, frameWidth):
  fqArray = hz_to_fft(sampleRate, frameWidth)

  return (list(map(lambda fq: int(np.round(fqArray[fq])), defaultFqTicks)), defaultFqTickLabels)


def plot_spectrum_line_component(data, sampleRate, rawData=[]):
  fig, (ax1, ax2) = plt.subplots(nrows=2)

  if len(rawData) > 0:
    t = np.arange(0, (1 / sampleRate) * np.size(rawData), 1/sampleRate)
    x = rawData
    ax1.plot(t, x)
    ax1.set_title("Raw Wave")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Amplitude")

  n = np.size(data)
  fr = (sampleRate / 2) * np.linspace(0, 1, n/2)
  X_m = data[:int(n/2)]

  assert len(X_m) == len(fr)

  ax2.plot(fr, X_m)
  ax2.set_title("Spectrum Line Component")
  ax2.set_xlabel("Frequency (Hz)")
  ax2.set_ylabel("Magnitude")
  ax2.tick_params(
      axis='y',          # changes apply to the y-axis
      which='both',      # both major and minor ticks are affected
      left=False,      # ticks along the bottom edge are off
      top=False,         # ticks along the top edge are off
      labelleft=False)  # labels along the bottom edge are off

  fig.tight_layout()
  return fig


def plot_correlation(data, sampleRate):
  fr = np.arange(0, len(data))

  plt.plot(fr, data)
  plt.show()

def plot_interpolated_correlation(interpolation, corelation, title="Correlation"):
  interp_x = np.linspace(0, len(corelation)-1, num=len(corelation)*10)
  x = np.arange(0, len(corelation))
  plt.plot(x, corelation, '-', interp_x, interpolation(interp_x), '--')
  plt.legend(['data', 'interpolated'], loc='best')
  plt.title(title)
  plt.show()

def plot_wave(sample_rate, normalized_data, wave_name):
  time_space = np.linspace(0, len(normalized_data) /
                           sample_rate, num=len(normalized_data))
  plt.figure()
  plt.title("wave " + wave_name)
  plt.xlabel("time (seconds)")
  plt.ylabel("amplitude[" + str(math.floor(normalized_data.min())) +
             ":" + str(math.ceil(normalized_data.max())) + "] (data)")
  plt.yticks(np.arange(math.floor(normalized_data.min()),
                       math.ceil(normalized_data.max()), 0.1))
  plt.plot(time_space, normalized_data)
  plt.show()


def plot_correlogram(data, spacing, sampleRate, title='Correlogram', show=True, showColorbar=True):
  fig, ax = plt.subplots()
  fig.suptitle(title, fontsize=16)
  H = np.array(data)
  image = ax.imshow(H.T, origin='lower', aspect='auto', interpolation='nearest')
  ax.set_ylabel('lag (samples)')
  ax.set_xlabel('time (seconds)')

  secLength = len(data)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))

  ax.set_ylim([0, len(H.T)])
  ax.set_xlim([0, len(H) - 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_cepstrogram(data, spacing, sampleRate, title='cepstrogram', show=True, showColorbar=True):
  fig, ax = plt.subplots()
  fig.suptitle(title, fontsize=16)
  H = np.array(data)
  image = ax.imshow(H.T, origin='lower', aspect='auto', interpolation='nearest')
  
  ax.set_ylabel('Quefrency')
  ax.set_xlabel('time (seconds)')

  secLength = len(data)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))

  ax.set_ylim([0, len(H.T)])
  ax.set_xlim([0, len(H) - 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_pitches(pitches, spacing, sampleRate, log=True, title='Estimation of f0', show=True):
  fig, ax = plt.subplots()
  fig.suptitle(title, fontsize=16)
  ax.plot(np.arange(len(pitches)), pitches)
  ax.set_ylabel('frequency (Hz)')
  if log: ax.set_yscale('log')
  ax.set_yticks(defaultFqTicks)
  ax.set_yticklabels(defaultFqTickLabels)
  ax.set_xlabel('time (seconds)')
  secLength = len(pitches)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))

  minHearableFq = 20
  ax.set_ylim([minHearableFq, 22049])
  ax.set_xlim([0, len(pitches)-1])
  ax.grid()

  if show: plt.show()
  return fig, ax


def plot_midi(notes, spacing, sampleRate, minNote=20, maxNote=120, title='Piano roll', show=True, showColorbar=True):
  fig, ax = plt.subplots()
  fig.suptitle(title, fontsize=16)
  image = ax.imshow(np.array(notes).T, origin='lower',
             aspect='auto', interpolation='nearest', cmap=pylab.cm.gray_r) # pylint: disable=no-member
  ax.set_xlabel('time (seconds)')
  secLength = len(notes)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))
  ax.set_ylim([minNote, maxNote])
  if showColorbar: fig.colorbar(image)

  if show: plt.show()

  return fig, ax

def plot_spectrogram(spectra, spacing, sampleRate, title='Spectrogram', show=True, showColorbar=True, transpose=True):
  fig, ax = plt.subplots()
  spectra = np.array(spectra)
  fig.suptitle(title, fontsize=16)
  if transpose:
    spectra = spectra.T
  frameWidth = len(spectra)
  image = ax.imshow(spectra, interpolation='nearest', origin='lower', aspect='auto')
  ax.set_yscale('log')
  ax.set_yticks(getFqTicks(sampleRate, frameWidth)[0])
  ax.set_yticklabels(getFqTicks(sampleRate, frameWidth)[1])

  ax.set_ylabel('frequency (Hz)')
  ax.set_xlabel('time (seconds)')
  
  secLength = len(spectra.T)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))

  minHearableFq = hz_to_fft(sampleRate, frameWidth)[20]
  ax.set_ylim([minHearableFq, frameWidth])
  ax.set_xlim([0, len(spectra.T)- 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_peaks(peaks, frameWidth, sampleRate, barwidth=3.0, show=True,):
  fig, ax = plt.subplots()
  ax.bar(peaks.nonzero()[0], peaks[peaks.nonzero()[0]], barwidth, color='black')
  ax.set_xticks(getFqTicks(sampleRate, frameWidth)[0][:-2])
  ax.set_xticklabels(getFqTicks(sampleRate, frameWidth)[1][:-2])
  ax.set_xlabel('frequency (Hz)')
  ax.set_ylabel('amplitude')
  if show: plt.show()
  return fig, ax

def plot_spectrogram_with_onsets(spectra, spacing, sampleRate, onsets, title='Spectrogram', show=True, showColorbar=True):
  fig, ax = plot_spectrogram(spectra, spacing, sampleRate, title, False, showColorbar)
  #TODO: https://stackoverflow.com/questions/12864294/adding-an-arbitrary-line-to-a-matplotlib-plot-in-ipython-notebook