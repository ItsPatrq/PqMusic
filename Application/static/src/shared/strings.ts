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
                transform: "Upload base track and generate track by Transform method"
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