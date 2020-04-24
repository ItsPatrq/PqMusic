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
    navBarTranscribe: "Wykonaj transkrypcję",
    navBarUtility: "Narzędzia",
    titleTranscribe: "Transkrypcja muzyki",
    titleUtilities: "Narzędzia",
    subTitleMonophonic: "Algorytmy przeznaczone dla sygnałów monofonicznych",
    subTitlePolyphonic: "Algorytmy przeznaczone dla sygnałów monofonicznych i polifonicznych (wynik w MIDI)",
    rowLabels: {
        transcription: {
            onesetsAndFrames: "Onesets and Frames",
            autoCorrelation: "Funkcja autokorelacji",
            cepstrum: "Analiza cepstralna",
            aclos: "ACLOS",
            jointMethodPertusa2008: "Metoda Pertusa i Iñesta (2008)",
            jointMethodPertusa2012: "Metoda Pertusa i Iñesta (2012)"
        },
        utils: {
            windowFunctions: "Pobierz wykres funkcji okna",
            fqMIDI: "Pomiar częstotliwości MIDI",
            spectrogram: "Spectrogram",
        }
    },
    modalLabels: {
        transcription: {
            autoCorrelationResult: "Wynik metody autokorelacji",
            cepstrumResult: "Wynik analizy cepstrum",
            aclosResult: "Wynik metody ACLOS",
            jointMethodPertusa2008: "Wynik metody Pertusa i Iñesta (2008)",
            jointMethodPertusa2012: "Wynik metody Pertusa i Iñesta (2012)"
        }
    },
    dropZoneDefaultMessage: "Przeciągnij i upuść lub kliknij aby wybrać plik do transkrypcji (wav lub mp3)",
    buttonLabelDownloadHannWindow: "Funkcja okna Hanna",
    buttonLabelDownloadHammingWindow: "Funkcja okna Hamminga",
    buttonLabelDownloadRectangleWindow: "Funkcja okna prostokątnego",
    pdfObjectFallback: "Użyta przeglądarka nie wspiera wyświetlania PDF"
}

const getStrings = () => pl;

export default getStrings();