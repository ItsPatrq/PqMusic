const eng = {
    navBarHome: "Home",
    navBarUploadMidi: "Upload MIDI",
    navBarTranscribe: "Transcribe",
    navBarUtility: "Utility",
    navBarGenerate: "Generate music",
    titleTranscribe: "Transcribe",
    titleUtilities: "Utility",
    rowLabels: {
        transcription: {
            onesetsAndFrames: "Onesets and Frames (Magenta default transcription model)",
            autoCorrelation: "AutoCorrelation method"
        },
        utils: {
            windowFunctions: "Download window function in plot",
            fqMIDI: "MIDI Frequency measurment",
            spectrogram: "Spectrogram",
        },
        generate: {
            unconditionedTransform: "Select premier for a unconditional transform model",
            melodyConditionedTransform: "Select melody to be accompanied by the model (if your MIDI file is polyphonic, the notes with highest pitch will be used as the melody).",
            lstm: "Generate piece by basic LSTM network",
            performanceRnn: "Generate piece by Performance RNN Model",
        }
    },
    dropZoneDefaultMessage: "Drag or click to upload file(s)",
    buttonLabelDownloadHannWindow: "Hann Window",
    buttonLabelDownloadHammingWindow: "Hamming Window",
    buttonLabelDownloadRectangleWindow: "Rectangle Window"
};

const pl = {
    ...eng,
    navBarHome: "Strona główna",
    navBarUploadMidi: "Prześlij MIDI",
    navBarTranscribe: "Wykonaj transkrypcję",
    navBarUtility: "Narzędzia",
    navBarGenerate: "Generuj muzykę",
    titleTranscribe: "Transkrypcja",
    titleUtilities: "Narzędzia",
    rowLabels: {
        transcription: {
            onesetsAndFrames: "Onesets and Frames (Bazowy modół tranksypcji projektu Magenta)",
            autoCorrelation: "Metoda Auto-korelacji",
            cepstrum: "Metoda oparta o cepstrum",
            aclos: "Metoda oparta o ACLOS",
            jointMethodPertusa2008: "Metoda łączona Pertusa i Iñesta (2008)",
            jointMethodPertusa2012: "Metoda łączona Pertusa i Iñesta (2012)"
        },
        utils: {
            windowFunctions: "Pobierz wykres funkcji okna",
            fqMIDI: "Pomiar częstotliwości MIDI",
            spectrogram: "Spectrogram",
        },
        generate: {
            unconditionedTransform: "Select premier for a unconditional transform model",
            melodyConditionedTransform: "Select melody to be accompanied by the model (if your MIDI file is polyphonic, the notes with highest pitch will be used as the melody).",
            lstm: "Generate piece by basic LSTM network",
            performanceRnn: "Generate piece by Performance RNN Model",
        }
    },
    modalLabels: {
        transcription: {
            autoCorrelationResult: "Wynik metody Auto-korelacji",
            cepstrumResult: "Wynik metody cepstrum",
            aclosResult: "Wynik metody ACLOS",
            jointMethodPertusa2008: "Wynik łączonej metody Pertusa i Iñesta (2008)",
            jointMethodPertusa2012: "Wynik łączonej metody Pertusa i Iñesta (2012)"
        }
    },
    dropZoneDefaultMessage: "Drag or click to upload file(s)",
    buttonLabelDownloadHannWindow: "Hann Window",
    buttonLabelDownloadHammingWindow: "Hamming Window",
    buttonLabelDownloadRectangleWindow: "Rectangle Window"
}

const getStrings = () => pl;

export default getStrings();