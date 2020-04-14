import superagent from 'superagent';
import { DownloadFile, DownloadFileFromBlob } from '../shared/utils';
import { DefaultToaster } from '../shared/components/toaster/DefaultToaster';

const env_url = process.env.NODE_ENV === "production" ? "https://pqmusic.herokuapp.com/" : "http://127.0.0.1:5000/"; 

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

class DataService implements DataService {
    constructor() {
        this.Spectrogram = this.Spectrogram.bind(this);
    }
    private GenericRequest(file: File, methodName: string, callback:(res:any) => any){
        const request = superagent.post(env_url + methodName).responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const response = res.xhr.response;
            callback(response);
        });
    }

    public GetThesisPaper() {
        return env_url + "Thesis"
    }

    public Spectrogram(file: File) {
        const request = superagent.post(env_url + "Spectrogram").responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "spectrogram.png", "image/png");
        });
    }

    public TranscribeByOnsetsFrames(file: File) {
        this.GenericRequest(file, "TranscribeByOnsetsAndFrames", (res:Blob) => {
            DownloadFileFromBlob(res, "transkrypcjaMetodaOnsetsAndFrames.mid", "audio/midi");
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
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const file = res.xhr.response.hann;
            DownloadFile(file, "HannWindow.png", "image/png");
        });
    }

    public HammingWindow() {
        const request = superagent.post(env_url + "HammingWindow").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

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
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "RectangleWindow.png", "image/png");
        });
    }

    public GenerateUnconditionedTransform(file: File) {
        const request = superagent.post(env_url + "GenerateTransformUnconditioned").responseType("blob");
        const formData = new FormData();
        formData.append('file', file);
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "out.midi", "audio/midi");
        });
    }

    public GenerateConditionedTransform(file: File) {
        const request = superagent.post(env_url + "GenerateTransformMelodyConditioned").responseType("blob");
        const formData = new FormData();
        request.send(formData);
        request.end((err, res) => {
            if(err || !res.ok) {
                DefaultToaster.show({ message: "Internal server error", className: "bp3-intent-danger"});
                return;
            }
            DefaultToaster.show({ message: "Success!", className: "bp3-intent-success" });

            const file = res.xhr.response;
            DownloadFile(file, "out.midi", "audio/midi");
        });
    }
}

export default new DataService();