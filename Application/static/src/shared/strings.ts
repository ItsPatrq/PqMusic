const eng = {
    navBarHome: "Home",
    navBarUploadMidi: "Upload MIDI",
    navBarTranscribe: "Transcribe",
    navBarUtility: "Utility",
    navBarGenerate: "Generate music",
    titleTranscribe: "Transcribe",
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
    rowLabels: {
        transcription: {
            onesetsAndFrames: "Onesets and Frames (Bazowy modół tranksypcji projektu Magenta)",
            autoCorrelation: "Metoda Auto-korelacji"
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
    dropZoneDefaultMessage: "Drag or click to upload file(s)",
    buttonLabelDownloadHannWindow: "Hann Window",
    buttonLabelDownloadHammingWindow: "Hamming Window",
    buttonLabelDownloadRectangleWindow: "Rectangle Window"
}

const getStrings = () => pl;

export default getStrings();