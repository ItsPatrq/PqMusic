const strings = {
    eng: {
        navBarHome: "Home",
        navBarUploadMidi: "Upload MIDI",
        navBarTranscribe: "Transcribe",
        navBarUtility: "Utility",
        navBarGenerate: "Generate music",
        rowLabels: {
            transcription: {
                onesetsAndFrames: "Onesets and Frames (Magenta default transcription model)",
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
    },
    pl: {

    }
}

const getStrings = () => strings.eng;

export default getStrings();