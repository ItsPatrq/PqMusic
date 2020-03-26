import superagent from 'superagent';
import { DownloadFile } from '../shared/utils';
import { DefaultToaster } from '../shared/components/toaster/DefaultToaster';

const env_url = "http://127.0.0.1:5000/"
type XMLHttpRequestParameters = string | Document | Blob | ArrayBufferView | ArrayBuffer | FormData | URLSearchParams | ReadableStream<Uint8Array> | null | undefined;

interface ITranscribeByAutoCorrelationResult {
    pitches: string,
    correlogram: string
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

    private GetRequest(methodName: string, callback?: (this: XMLHttpRequest) => any, responseType: XMLHttpRequestResponseType = "json") {
        let request = new XMLHttpRequest();
        const url = env_url + methodName;
        request.open('POST', url, true);
        request.onload = callback || null;
        request.onerror = function (this: XMLHttpRequest) {
            console.error(`Error occurred during sending request ${url}`);
        }
        request.responseType = responseType;
        request.setRequestHeader('Content-type', 'audio/mp3');
        return request;
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
        const request = superagent.post(env_url + "TranscribeByOnsetsFrames").responseType("blob");
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
            DownloadFile(file, "out.mid", "audio/midi");
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

    public TranscribeByCepstrum(file: File, callback: (result: ITranscribeByAutoCorrelationResult) => void) {
        this.GenericRequest(file, "TranscribeByCepstrum", (res:Blob) => {
            const reader = new FileReader();
            reader.onload = () => {
                const x = JSON.parse(reader.result as string)
                callback(x as ITranscribeByAutoCorrelationResult)
            }
            reader.readAsText(res);
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