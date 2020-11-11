import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../../dataService/DataService';
import { DefaultToaster } from '../../shared/components/toaster/DefaultToaster';
import { IStrings, LanguageContext } from '../../shared/languageContext';


export const Spectrogram: FC = () => {
    const getDropzoneContent = (strings: IStrings) => (props: DropzoneState) => (
        <section>
            <div {...props.getRootProps()}>
                <input {...props.getInputProps()} />
                <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>
            </div>
        </section>
    );
    const getHandleChange = (strings: IStrings) => (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        if (acceptedFiles.length > 0) {
            DataService.Spectrogram(acceptedFiles[0], strings)
        }
        if (rejectedFiles.length > 0) {
            DefaultToaster.show({ message: strings.serverError, className: "bp3-intent-danger"});

            console.log(rejectedFiles, event)
        }
    }
    const getContent = (strings: IStrings) => (
        <div className="PqM-Utility_spectrogram">
            <Dropzone
                accept={['audio/mp3', 'audio/wav']}
                onDrop={getHandleChange(strings)}
                multiple={false}
            >
                {getDropzoneContent(strings)}
            </Dropzone>
        </div>
    )

    return (
        <LanguageContext.Consumer>
            {({strings}) => (
                <RowFlex
                    children={getContent(strings)}
                    label={strings.rowLabels.utils.spectrogram}
                />
            )}
        </LanguageContext.Consumer>
    );
}

export default Spectrogram;