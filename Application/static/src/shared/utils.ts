export const DownloadFile = (file:File, fileName:string, type:string) => {
    var blob = new Blob([file], { type: type });
    var link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
}