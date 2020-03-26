#from pydub import AudioSegment
import ntpath
import numpy as np
import matplotlib.pyplot as plt
import math
from .general import hz_to_fourier, fourier_to_hz, hz_to_fft
import pylab
import networkx as nx

strings = {
  'pl': {
    "audioWave": "Fala dźwiękowa",
    "time": "Czas (w sekundach)",
    "timeSamples": "Czas (w ilości sampli)",
    "amplitude":  "Amplituda",
    "spectrumLineComponent": "Liniowy komponent widma",
    "fq": "Częstotliwość (w Hz)",
    "magnitude": "Wielkość",
    "data": "Dane",
    "interpolated": "Interpolacja",
    "lag": "Opóźnienie (w ilości sampli)",
    "correlogram": "Korelogram",
    "quefrency": "Quefrency",
    "cepstrogram": "Cepstrogram",
    "f0Estimation": "Estymacja F0",
    "pianoRoll": "Rolka Pianina",
    "spectrogram": "Spektrogram",
    "peaks": "Piki",
    "aclos": "ACLOS",
    "correlation": "Korelacja"
  },
  'eng': {
    "audioWave": "Audio wave",
    "time": "Time (in seconds)",
    "timeSamples": "Time (in samples)",
    "amplitude":  "Amplitude",
    "spectrumLineComponent": "Spectrum Line Component",
    "fq": "Frequency (in Hz)",
    "magnitude": "Magnitude",
    "data": "Data",
    "interpolated": "Interpolated",
    "lag": "Lag (in samples)",
    "correlogram": "Correlogram",
    "quefrency": "Quefrency",
    "cepstrogram": "Cepstrogram",
    "f0Estimation": "Estimation of f0",
    "pianoRoll": "Piano Roll",
    "spectrogram": "Spectrogram",
    "peaks": "Peaks",
    "aclos": "ACLOS",
    "correlation": "Correlation"
  }
}

ticksFontSize = 18
labelsFontSize = 32

defaultSubplotProps = {
    "figsize": (18,12)
}

def getStr(language, strName):
  return strings.get(language).get(strName)

defaultFqTicks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
defaultFqTickLabels = [20, 50, 100, 200, 500, '1k', '2k', '5k', '10k', '20k']

def getTimeTicks(spacing, sampleRate, secLength):
  ticks = [0]
  fullSecs = int(math.floor(secLength))  

  for t in np.arange(3, fullSecs - 3, 3):
    ticks.append(t*sampleRate/spacing)
  ticks.append(int(secLength*sampleRate/spacing) - 1)
  
  return ticks

def getTimeTickLabels(secLength):
  fullSecs = int(math.floor(secLength))
  tickLabels = list(np.concatenate(([0], np.arange(3, fullSecs - 3, 3), [round(secLength, 3)])))
  return tickLabels

def getFqTicks(sampleRate, frameWidth):
  fqArray = hz_to_fft(sampleRate, frameWidth)

  return (list(map(lambda fq: int(np.round(fqArray[fq])), defaultFqTicks)), defaultFqTickLabels)


def plot_spectrum_line_component(data, sampleRate, rawData=[], language = "eng"):
  fig, (ax1, ax2) = plt.subplots(nrows=2, **defaultSubplotProps)

  if len(rawData) > 0:
    t = np.arange(0, (1 / sampleRate) * np.size(rawData), 1/sampleRate)
    x = rawData
    ax1.plot(t, x)
    ax1.set_title(getStr(language, "audioWave"))
    ax1.set_xlabel(getStr(language, "time"))
    ax1.set_ylabel(getStr(language, "amplitude"))

  n = np.size(data)
  fr = (sampleRate / 2) * np.linspace(0, 1, n/2)
  X_m = data[:int(n/2)]

  assert len(X_m) == len(fr)

  ax2.plot(fr, X_m)
  ax2.set_title(getStr(language, "spectrumLineComponent"), fontsize=labelsFontSize)
  ax2.set_xlabel(getStr(language, "fq"), fontsize=labelsFontSize)
  ax2.set_ylabel(getStr(language, "magnitude"), fontsize=labelsFontSize)
  ax2.tick_params(
      axis='y',          # changes apply to the y-axis
      which='both',      # both major and minor ticks are affected
      left=False,      # ticks along the bottom edge are off
      top=False,         # ticks along the top edge are off
      labelleft=False)  # labels along the bottom edge are off

  fig.tight_layout()
  return fig


def plot_spectrum_line_component_only(data, sampleRate, show=True, language = "eng"):
  n = np.size(data)
  fr = (sampleRate / 2) * np.linspace(0, 1, n/2)
  X_m = data[:int(n/2)]
  fig, ax = plt.subplots(**defaultSubplotProps)
  ax.plot(fr, X_m)
  ax.set_title(getStr(language, "spectrumLineComponent"), fontsize=labelsFontSize)
  ax.set_xlabel(getStr(language, "fq"), fontsize=labelsFontSize)
  ax.set_ylabel(getStr(language, "magnitude"), fontsize=labelsFontSize)
  ax.tick_params(
      axis='y',          # changes apply to the y-axis
      which='both',      # both major and minor ticks are affected
      left=False,      # ticks along the bottom edge are off
      top=False,         # ticks along the top edge are off
      labelleft=False)  # labels along the bottom edge are off

  fig.tight_layout()
  if show: plt.show()
  return fig, ax

def plot_spectrum_line_components(dataBase, data1, data2, data3, sampleRate, show=True, language = "eng"):
  n = np.size(dataBase)
  fr = (sampleRate / 2) * np.linspace(0, 1, n/2)
  X_m = dataBase[:int(n/2)]
  x1_m = data1[:int(n/2)]
  x2_m = data2[:int(n/2)]
  x3_m = data3[:int(n/2)]
  fig, ax = plt.subplots(**defaultSubplotProps)
  ax.plot(fr, X_m, '-', fr, x1_m, '--',fr, x2_m, '--', fr, x3_m, '--')
  ax.set_title(getStr(language, "spectrumLineComponent"), fontsize=labelsFontSize)
  ax.set_xlabel(getStr(language, "fq"), fontsize=labelsFontSize)
  ax.set_ylabel(getStr(language, "magnitude"), fontsize=labelsFontSize)
  plt.legend(["Em3", "E3", "G3", "B3"], loc='best')
  ax.tick_params(
      axis='y',          # changes apply to the y-axis
      which='both',      # both major and minor ticks are affected
      left=False,      # ticks along the bottom edge are off
      top=False,         # ticks along the top edge are off
      labelleft=False)  # labels along the bottom edge are off

  fig.tight_layout()
  if show: plt.show()
  return fig, ax



def plot_correlation(data, sampleRate, language='eng'):
  plt.figure()
  plt.title(getStr(language, "correlation"), fontsize=labelsFontSize)
  plt.xlabel(getStr(language, "lag"), fontsize=labelsFontSize)
  plt.ylabel(getStr(language, "correlation"), fontsize=labelsFontSize)

  plt.xticks(np.arange(0, len(data), 250), np.arange(0, len(data), 250),fontsize=ticksFontSize)
  plt.yticks(fontsize=ticksFontSize)
  plt.plot(np.arange(0, len(data)), data)
  plt.show()

def plot_interpolated_correlation(interpolation, corelation, title="Correlation", language = "eng"):
  interp_x = np.linspace(0, len(corelation)-1, num=len(corelation)*10)
  x = np.arange(0, len(corelation))
  plt.plot(x, corelation, '-', interp_x, interpolation(interp_x), '--')
  plt.legend([getStr(language, "data"), getStr(language, "interpolated")], loc='best')
  plt.title(getStr(language, "aclos"), fontsize=labelsFontSize)
  plt.xlabel(getStr(language, "lag"), fontsize=labelsFontSize)
  plt.ylabel(getStr(language, "magnitude"), fontsize=labelsFontSize)
  plt.xticks(fontsize=ticksFontSize)
  plt.yticks(fontsize=ticksFontSize)
  plt.show()

def plot_wave(normalized_data, sample_rate, wave_name, language = "eng", x_axis_as_samples = False):
  time_space = np.linspace(0, len(normalized_data) /
                           sample_rate, num=len(normalized_data))
  plt.figure()
  plt.title(getStr(language, "audioWave") + " " + wave_name)
  plt.ylabel(getStr(language, "amplitude") + " [" + str(math.floor(normalized_data.min())) +
             ":" + str(math.ceil(normalized_data.max())) + "]", fontsize=labelsFontSize)
  plt.yticks(np.arange(math.floor(normalized_data.min()),
                       math.ceil(normalized_data.max()), 0.1), fontsize=ticksFontSize)
  secLength = len(normalized_data)/sample_rate

  if x_axis_as_samples:
    plt.xticks(np.arange(0, len(normalized_data), 250), np.arange(0, len(normalized_data), 250),fontsize=ticksFontSize)
    plt.plot(np.arange(0, len(normalized_data)), normalized_data)
    plt.xlabel(getStr(language, "timeSamples"), fontsize=labelsFontSize)

  else:
    plt.xticks(getTimeTickLabels(secLength), getTimeTickLabels(secLength),fontsize=ticksFontSize)
    plt.plot(time_space, normalized_data)
    plt.xlabel(getStr(language, "time"), fontsize=labelsFontSize)

  plt.show()


def plot_correlogram(data, spacing, sampleRate, show=True, showColorbar=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  fig.suptitle(getStr(language, "correlogram"), fontsize=labelsFontSize)
  H = np.array(data)
  image = ax.imshow(H.T, origin='lower', aspect='auto', interpolation='nearest')
  ax.set_ylabel(getStr(language, "lag"), fontsize=labelsFontSize)
  ax.set_xlabel(getStr(language, "time"), fontsize=labelsFontSize)

  secLength = len(data)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength), fontsize=ticksFontSize)
  ax.set_yticks(np.arange(0, len(H.T), 200))
  ax.set_yticklabels(np.arange(0, len(H.T), 200), fontsize=ticksFontSize)


  ax.set_yticklabels(ax.get_yticklabels(), fontsize=ticksFontSize)

  ax.set_ylim([0, len(H.T)])
  ax.set_xlim([0, len(H) - 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_cepstrogram(data, spacing, sampleRate, show=True, showColorbar=True, transpose=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  fig.suptitle(getStr(language, "cepstrogram"), fontsize=labelsFontSize)
  H = np.array(data)
  if transpose: H = H.T
  image = ax.imshow(H, origin='lower', aspect='auto', interpolation='nearest')
  
  ax.set_ylabel(getStr(language, "quefrency"), fontsize=labelsFontSize)
  ax.set_xlabel(getStr(language, "time"), fontsize=labelsFontSize)

  secLength = len(data)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength), fontsize=ticksFontSize)
  ax.set_yticks(np.arange(0, len(H), 100))
  ax.set_yticklabels(np.arange(0, len(H), 100), fontsize=ticksFontSize)

  ax.set_ylim([0, len(H)])
  ax.set_xlim([0, len(H.T) - 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_pitches(pitches, spacing, sampleRate, log=True, show=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  fig.suptitle(getStr(language,"f0Estimation"), fontsize=labelsFontSize)
  ax.plot(np.arange(len(pitches)), pitches, linewidth=2)
  ax.set_ylabel(getStr(language, "fq"), fontsize=labelsFontSize)
  if log: ax.set_yscale("log")
  ax.set_yticks(defaultFqTicks)
  ax.set_yticklabels(defaultFqTickLabels, fontsize=ticksFontSize)
  ax.set_xlabel(getStr(language, "time"), fontsize=labelsFontSize)
  secLength = len(pitches)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength), fontsize=ticksFontSize)

  minHearableFq = 20
  ax.set_ylim([minHearableFq, 22049])
  ax.set_xlim([0, len(pitches)-1])
  ax.grid()
  if show: plt.show()
  return fig, ax


def plot_midi(notes, spacing, sampleRate, minNote=20, maxNote=120, show=True, showColorbar=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  fig.suptitle(getStr(language, "pianoRoll"), fontsize=16)
  image = ax.imshow(np.array(notes).T, origin='lower',
             aspect='auto', interpolation='nearest', cmap=pylab.cm.gray_r) # pylint: disable=no-member
  ax.set_xlabel(getStr(language, "time"))
  secLength = len(notes)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength))
  ax.set_ylim([minNote, maxNote])
  if showColorbar: fig.colorbar(image)

  if show: plt.show()

  return fig, ax

def plot_spectrogram(spectra, spacing, sampleRate, show=True, showColorbar=True, transpose=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  spectra = np.array(spectra)
  fig.suptitle(getStr(language, "spectrogram"), fontsize=labelsFontSize)
  if transpose:
    spectra = spectra.T
  frameWidth = len(spectra)
  image = ax.imshow(spectra, interpolation='nearest', origin='lower', aspect='auto')
  ax.set_yscale('log')
  ax.set_yticks(getFqTicks(sampleRate, frameWidth)[0])
  ax.set_yticklabels(getFqTicks(sampleRate, frameWidth)[1], fontsize=ticksFontSize)

  ax.set_ylabel(getStr(language, "fq"), fontsize=labelsFontSize)
  ax.set_xlabel(getStr(language, "time"), fontsize=labelsFontSize)
  
  secLength = len(spectra.T)*spacing/sampleRate
  ax.set_xticks(getTimeTicks(spacing, sampleRate, secLength))
  ax.set_xticklabels(getTimeTickLabels(secLength), fontsize=ticksFontSize)

  minHearableFq = hz_to_fft(sampleRate, frameWidth)[20]
  ax.set_ylim([minHearableFq, frameWidth])
  ax.set_xlim([0, len(spectra.T)- 1])

  if showColorbar: fig.colorbar(image)

  if show: plt.show()
  return fig, ax

def plot_peaks(peaks, frameWidth, sampleRate, barwidth=3.0, show=True, language = "eng"):
  fig, ax = plt.subplots(**defaultSubplotProps)
  fig.suptitle(getStr(language, "peaks"), fontsize=16)
  ax.bar(peaks.nonzero()[0], peaks[peaks.nonzero()[0]], barwidth, color='black')
  ax.set_xticks(getFqTicks(sampleRate, frameWidth)[0][:-2])
  ax.set_xticklabels(getFqTicks(sampleRate, frameWidth)[1][:-2])
  ax.set_xlabel(getStr(language, "fq"))
  ax.set_ylabel(getStr(language, "amplitude"))
  if show: plt.show()
  return fig, ax

def plot_spectrogram_with_onsets(spectra, spacing, sampleRate, onsets, title='Spectrogram', show=True, showColorbar=True):
  fig, ax = plot_spectrogram(spectra, spacing, sampleRate, title, False, showColorbar)
  #TODO: https://stackoverflow.com/questions/12864294/adding-an-arbitrary-line-to-a-matplotlib-plot-in-ipython-notebook

def plot_pitch_tracking(path, G):
  pos = nx.spring_layout(G)
  nx.draw(G,pos,node_color='gray', node_size=500)
  print(G.edges())
  nx.draw_networkx_edge_labels(G,alpha=0.7, pos=pos, font_size=6, font_color='k')
  nx.draw_networkx_labels(G,pos=pos, font_size=14, font_weight="bold", font_color='k')

  nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
  plt.axis('equal')
  plt.show()