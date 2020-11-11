import superagent from 'superagent';
import { DownloadFile, DownloadFileFromBlob } from '../shared/utils';
import { DefaultToaster } from '../shared/components/toaster/DefaultToaster';
import { IStrings } from '../shared/languageContext';

let env_url = window.location.href;
if(process.env.REACT_APP_ENV === "local") {
    env_url = "http://localhost:5000/";
}

interface ITranscribeByAutoCorrelationResult {
    pitches: string,
    correlogram: string
}

interface ITranscribeByCepstrumResult {
    pitches: string,
    cepstrogram: string,
    spectrogram: string,
    logSpectrogram: string
}

interface ITranscribeByAclosResult {
    pitches: string,
    correlogram: string,
    spectrogram: string,
}

class DataService {
    constructor() {
        this.Spectrogram = this.Spectrogram.bind(this);
    }
    private key = 0;
    private GetNewKey() {
        this.key += 1;
        return this.key.toString();
    }
    private GenericRequest(file: File, methodName: string, callback:(res:any) => any, strings: IStrings){
        const currKey = this.GetNewKey();
        DefaultToaster.show({ message: strings.processing, className: "bp3-intent-primary", timeout: 0 }, currKey);
        const request = superagent.post(env_url + methodName).responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.dismiss(currKey);
                DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: strings.processingComplete, className: "bp3-intent-success" });

            const response = res.xhr.response;
            callback(response);
            DefaultToaster.dismiss(currKey);
        });
    }

    public Spectrogram(file: File, strings: IStrings) {
        const currKey = this.GetNewKey();
        DefaultToaster.show({ message: "Przetwarzanie...", className: "bp3-intent-primary", timeout: 0 }, currKey);
        const request = superagent.post(env_url + "Spectrogram").responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.dismiss(currKey);
                DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: strings.processingComplete, className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "spectrogram.png", "image/png");
            DefaultToaster.dismiss(currKey);
        });
    }

    public TranscribeByOnsetsFrames(file: File, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByOnsetsAndFrames", (res:Blob) => {
            if(res.type === "text/html") {
                const reader = new FileReader();
                reader.readAsText(res);
                reader.onload = function() {
                    DefaultToaster.show({ message: reader.result, className: "bp3-intent-danger"});
                };
            } else {
                DownloadFileFromBlob(res, `${strings.plots.onsetsAndFramesFile}.mid`, "audio/midi");
            }
        }, strings);
    }

    public TranscribeByAutoCorrelation(file: File, callback: (result: ITranscribeByAutoCorrelationResult) => void, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByAutoCorrelation", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByAutoCorrelationResult)
            }
            reader.readAsText(res);
        }, strings);
    }

    public TranscribeByCepstrum(file: File, callback: (result: ITranscribeByCepstrumResult) => void, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByCepstrum", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByCepstrumResult)
            }
            reader.readAsText(res);
        }, strings);
    }

    public TranscribeByAclos(file: File, callback: (result: ITranscribeByAclosResult) => void, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByAclos", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByAclosResult)
            }
            reader.readAsText(res);
        }, strings);
    }

    public TranscribeByGenerativeMethodPertusa2008(file: File, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByPertusa2008", (res:Blob) => {
            DownloadFileFromBlob(res, `${strings.plots.pertusaInesta2008File}.mid`, "audio/midi");
        }, strings);
    }


    public TranscribeByGenerativeMethodPertusa2012(file: File, strings: IStrings) {
        this.GenericRequest(file, "TranscribeByPertusa2012", (res:Blob) => {
            DownloadFileFromBlob(res, `${strings.plots.pertusaInesta2012File}.mid`, "audio/midi");
        }, strings);
    }

    public HannWindow(strings: IStrings) {
        const request = superagent.post(env_url + "HannWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: strings.processingComplete, className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "HannWindow.png", "image/png");
        });
    }

    public HammingWindow(strings: IStrings) {
        const request = superagent.post(env_url + "HammingWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: strings.processingComplete, className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "HammingWindow.png", "image/png");
        });
    }

    public RectangleWindow(strings: IStrings) {
        const request = superagent.post(env_url + "RectangleWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: strings.processingComplete, className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "RectangleWindow.png", "image/png");
        });
    }
}

export default new DataService();