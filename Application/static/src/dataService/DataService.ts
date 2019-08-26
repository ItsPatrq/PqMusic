import superagent from 'superagent';

const env_url = "http://127.0.0.1:5000/"
type XMLHttpRequestParameters = string | Document | Blob | ArrayBufferView | ArrayBuffer | FormData | URLSearchParams | ReadableStream<Uint8Array> | null | undefined;



class DataService implements DataService {
    constructor() {
        this.SayHello = this.SayHello.bind(this);
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

    public SayHello(file: File) {
        const request = superagent.post(env_url + "SayHello");
        const formData = new FormData();
        formData.append('file', file)
        request.send(formData);
        request.end()
    }
}

export default new DataService();