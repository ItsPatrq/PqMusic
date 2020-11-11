import React from "react";

enum languagesEnum {
    eng,
    pl
}

export interface IStrings {
    navBarHome: string
    navBarUploadMidi: string
    navBarTranscribe: string
    navBarUtility: string
    navBarGenerate: string
    titleTranscribe: string
    titleUtilities: string
    subTitleMonophonic: string
    subTitlePolyphonic: string
    rowLabels: {
        transcription: {
            onsetsAndFrames: string
            autoCorrelation: string
            cepstrum: string
            aclos: string
            GenerativeMethodPertusa2008: string
            GenerativeMethodPertusa2012: string
        },
        utils: {
            windowFunctions: string
            fqMIDI: string
            spectrogram: string
        }
    },
    modalLabels: {
        transcription: {
            autoCorrelationResult: string
            cepstrumResult: string
            aclosResult: string
            GenerativeMethodPertusa2008: string
            GenerativeMethodPertusa2012: string
        }
    },
    plots: {
        correlogram: string,
        pitches: string,
        powerSpec: string,
        logPowSpec: string,
        cepstrogram: string,
        onsetsAndFramesFile: string,
        pertusaInesta2008File: string,
        pertusaInesta2012File: string,
    }
    dropZoneDefaultMessage: string
    buttonLabelDownloadHannWindow: string
    buttonLabelDownloadHammingWindow: string
    buttonLabelDownloadRectangleWindow: string
    pdfObjectFallback: string,
    serverError: string,
    processing: string,
    processingComplete: string,
    homePage: string
}

const eng: IStrings= {
    navBarHome: "Home",
    navBarUploadMidi: "Upload MIDI",
    navBarTranscribe: "Transcribe",
    navBarUtility: "Utility",
    navBarGenerate: "Generate music",
    titleTranscribe: "Transcribe",
    titleUtilities: "Utility",
    subTitleMonophonic: "Algorithms for monophonic sounds",
    subTitlePolyphonic: "Algorithms for monophonic and polyphonic sounds (result in MIDI)",
    plots: {
        correlogram: "correlogram",
        pitches: "pitches",
        powerSpec: "power spectrogram",
        logPowSpec: "logarithm power spectrogram",
        cepstrogram: "cepstrogram",
        onsetsAndFramesFile: "onsetsAndFramesTranscriptionMethod",
        pertusaInesta2008File: "pertusaInesta2008TranscriptionMethod",
        pertusaInesta2012File: "pertusaInesta2012TranscriptionMethod",
    },
    rowLabels: {
        transcription: {
            onsetsAndFrames: "Onsets and Frames (Magenta default transcription model)",
            autoCorrelation: "AutoCorrelation method",
            cepstrum: "Cepstral analysis",
            aclos: "ACLOS",
            GenerativeMethodPertusa2008: "Pertusa and Iñest method (2008)",
            GenerativeMethodPertusa2012: "Pertusa and Iñest method (2012)"
        },
        utils: {
            windowFunctions: "Download window function in plot",
            fqMIDI: "MIDI Frequency measurment",
            spectrogram: "Spectrogram",
        }
    },
    modalLabels: {
        transcription: {
            autoCorrelationResult: "Results of autocorrelation method",
            cepstrumResult: "Results of cepstral analysis",
            aclosResult: "Results of ACLOS method",
            GenerativeMethodPertusa2008: "Results of Pertusa and Iñest method (2008)",
            GenerativeMethodPertusa2012: "Results of Pertusa and Iñest method (2012)"
        }
    },
    dropZoneDefaultMessage: "Drag or click to upload file(s) for transcription (wav or mp3)",
    buttonLabelDownloadHannWindow: "Hann Window",
    buttonLabelDownloadHammingWindow: "Hamming Window",
    buttonLabelDownloadRectangleWindow: "Rectangle Window",
    pdfObjectFallback: "Current browser does not support PDF preview",
    serverError: "Internal server error",
    processing: "Processing request...",
    processingComplete: "Processing complete!",
    homePage: "This application allows to test how algorithms for music transcription works.\nAll implemented methods are available in \"Transcribe\" section."
};

const pl: IStrings = {
    ...eng,
    navBarHome: "Strona główna",
    navBarTranscribe: "Wykonaj transkrypcję",
    navBarUtility: "Narzędzia",
    titleTranscribe: "Transkrypcja muzyki",
    titleUtilities: "Narzędzia",
    subTitleMonophonic: "Algorytmy przeznaczone dla sygnałów monofonicznych",
    subTitlePolyphonic: "Algorytmy przeznaczone dla sygnałów monofonicznych i polifonicznych (wynik w MIDI)",
    plots: {
        correlogram: "korelogram",
        pitches: "tony",
        powerSpec: "spektrogram mocy",
        logPowSpec: "logarytm spektrogramu mocy",
        cepstrogram: "cepstrogram",
        onsetsAndFramesFile: "transkrypcjaMetodaOnsetsAndFrames",
        pertusaInesta2008File: "transkrypcjaMetodaPertusaInesta2008",
        pertusaInesta2012File: "transkrypcjaMetodaPertusaInesta2012",
    },
    rowLabels: {
        transcription: {
            onsetsAndFrames: "onsets and Frames",
            autoCorrelation: "Funkcja autokorelacji",
            cepstrum: "Analiza cepstralna",
            aclos: "ACLOS",
            GenerativeMethodPertusa2008: "Metoda Pertusa i Iñesta (2008)",
            GenerativeMethodPertusa2012: "Metoda Pertusa i Iñesta (2012)"
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
            GenerativeMethodPertusa2008: "Wynik metody Pertusa i Iñesta (2008)",
            GenerativeMethodPertusa2012: "Wynik metody Pertusa i Iñesta (2012)"
        }
    },
    dropZoneDefaultMessage: "Przeciągnij i upuść lub kliknij aby wybrać plik do transkrypcji (wav lub mp3)",
    buttonLabelDownloadHannWindow: "Funkcja okna Hanna",
    buttonLabelDownloadHammingWindow: "Funkcja okna Hamminga",
    buttonLabelDownloadRectangleWindow: "Funkcja okna prostokątnego",
    pdfObjectFallback: "Użyta przeglądarka nie wspiera wyświetlania PDF",
    serverError: "Błąd serwera",
    processing: "Przetwarzanie...",
    processingComplete: "Przetwarzanie zakończone!",
    homePage: "Ta aplikacja pozwala przetestować działanie algorytmów transkrypcji muzyki.\nWszystkie zaimplementowane metody są dostępne w sekcji \"Wykonaj transkrypcję\"."

}

const strings = {
    [languagesEnum.pl]: pl,
    [languagesEnum.eng]: eng
};

const LanguageContext = React.createContext(
    {
        strings: strings[languagesEnum.eng],
        language: languagesEnum.eng
    }
);
LanguageContext.displayName = "LanguageContext";

const getContextValue = (language: languagesEnum) => ({
    strings: strings[language],
    language: language
});
export { languagesEnum, LanguageContext };
export default getContextValue;