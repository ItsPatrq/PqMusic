import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../../dataService/DataService';
import { DefaultToaster } from '../../shared/components/toaster/DefaultToaster';


export const Spectrogram: FC = () => {
    const dropzoneContent = (props: DropzoneState) => (
        <section>
            <div {...props.getRootProps()}>
                <input {...props.getInputProps()} />
                <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>
            </div>
        </section>
    )
    const handleChange = (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        if (acceptedFiles.length > 0) {
            DataService.Spectrogram(acceptedFiles[0])
        }
        if (rejectedFiles.length > 0) {
            DefaultToaster.show({ message: "Błąd serwera", className: "bp3-intent-danger"});

            console.log(rejectedFiles, event)
        }
    }
    const content = (
        <div className="PqM-Utility_spectrogram">
            <Dropzone
                accept={['audio/mp3', 'audio/wav']}
                onDrop={handleChange}
                multiple={false}
            >
                {dropzoneContent}
            </Dropzone>
        </div>
    )

    return (
        <RowFlex
            children={content}
            label={strings.rowLabels.utils.spectrogram}
        />
    );
}

export default Spectrogram;