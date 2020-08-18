import superagent from 'superagent';
import { DownloadFile, DownloadFileFromBlob } from '../shared/utils';
import { DefaultToaster } from '../shared/components/toaster/DefaultToaster';

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
    private GenericRequest(file: File, methodName: string, callback:(res:any) => any){
        const currKey = this.GetNewKey();
        DefaultToaster.show({ message: "Przetwarzanie...", className: "bp3-intent-primary", timeout: 0 }, currKey);
        const request = superagent.post(env_url + methodName).responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.dismiss(currKey);
                DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Przetwarzanie zakończone!", className: "bp3-intent-success" });

            const response = res.xhr.response;
            callback(response);
            DefaultToaster.dismiss(currKey);
        });
    }

    public GetThesisPaper() {
        return env_url + "Thesis"
    }

    public Spectrogram(file: File) {
        const currKey = this.GetNewKey();
        DefaultToaster.show({ message: "Przetwarzanie...", className: "bp3-intent-primary", timeout: 0 }, currKey);
        const request = superagent.post(env_url + "Spectrogram").responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.dismiss(currKey);
                DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Przetwarzanie zakończone!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "spectrogram.png", "image/png");
            DefaultToaster.dismiss(currKey);
        });
    }

    public TranscribeByOnsetsFrames(file: File) {
        this.GenericRequest(file, "TranscribeByOnsetsAndFrames", (res:Blob) => {
            if(res.type === "text/html") {
                const reader = new FileReader();
                reader.readAsText(res);
                reader.onload = function() {
                    DefaultToaster.show({ message: reader.result, className: "bp3-intent-danger"});
                };
            } else {
                DownloadFileFromBlob(res, "transkrypcjaMetodaOnsetsAndFrames.mid", "audio/midi");
            }
        });
    }

    public TranscribeByAutoCorrelation(file: File, callback: (result: ITranscribeByAutoCorrelationResult) => void) {
        this.GenericRequest(file, "TranscribeByAutoCorrelation", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByAutoCorrelationResult)
            }
            reader.readAsText(res);
        });
    }

    public TranscribeByCepstrum(file: File, callback: (result: ITranscribeByCepstrumResult) => void) {
        this.GenericRequest(file, "TranscribeByCepstrum", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByCepstrumResult)
            }
            reader.readAsText(res);
        });
    }

    public TranscribeByAclos(file: File, callback: (result: ITranscribeByAclosResult) => void) {
        this.GenericRequest(file, "TranscribeByAclos", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByAclosResult)
            }
            reader.readAsText(res);
        });
    }

    public TranscribeByJointMethodPertusa2008(file: File) {
        this.GenericRequest(file, "TranscribeByPertusa2008", (res:Blob) => {
            DownloadFileFromBlob(res, "transkrypcjaMetodaPertusaInesta2008.mid", "audio/midi");
        });
    }


    public TranscribeByJointMethodPertusa2012(file: File) {
        this.GenericRequest(file, "TranscribeByPertusa2012", (res:Blob) => {
            DownloadFileFromBlob(res, "transkrypcjaMetodaPertusaInesta2012.mid", "audio/midi");
        });
    }

    public HannWindow() {
        const request = superagent.post(env_url + "HannWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Przetwarzanie zakończone!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "HannWindow.png", "image/png");
        });
    }

    public HammingWindow() {
        const request = superagent.post(env_url + "HammingWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Przetwarzanie zakończone!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "HammingWindow.png", "image/png");
        });
    }

    public RectangleWindow() {
        const request = superagent.post(env_url + "RectangleWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Przetwarzanie zakończone!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "RectangleWindow.png", "image/png");
        });
    }
}

export default new DataService();