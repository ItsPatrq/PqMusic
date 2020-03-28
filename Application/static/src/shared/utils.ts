export const DownloadFile = (file:File, fileName:string, type:string) => {
    const blob = new Blob([file], { type: type });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
}

export const DownloadFileFromBlob= (blob:Blob, fileName:string, type:string) => {
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
}