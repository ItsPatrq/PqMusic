import superagent from 'superagent';
import { DownloadFile } from '../shared/utils';
import { DefaultToaster } from '../shared/components/toaster/DefaultToaster';

const env_url = "http://127.0.0.1:5000/"
type XMLHttpRequestParameters = string | Document | Blob | ArrayBufferView | ArrayBuffer | FormData | URLSearchParams | ReadableStream<Uint8Array> | null | undefined;



class DataService implements DataService {
    constructor() {
        this.Spectrogram = this.Spectrogram.bind(this);
    }
    private GetRequest(methodName: string, callback?: (this: XMLHttpRequest) => any, responseType: XMLHttpRequestResponseType = "json") {
        let request = new XMLHttpRequest();
        const url = env_url + methodName;
        request.open('POST', url, true);
        request.onload = callback || null;
        request.onerror = function (this: XMLHttpRequest) {
            console.error(`Error occured during sending request ${url}`);
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
}

export default new DataService();