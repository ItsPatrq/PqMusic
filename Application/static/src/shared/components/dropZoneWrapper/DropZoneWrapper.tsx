import React, { FC } from 'react';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import { LanguageContext } from '../../languageContext';
import { DefaultToaster } from '../toaster/DefaultToaster';

export type DropZoneWrapperProps = {
    callback(files: File[]): any,
    multiple: boolean
}

export const DropZoneWrapper: FC<DropZoneWrapperProps> = ({ callback, multiple = false }) => {

    const getDefaultOnDrop = (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        if (acceptedFiles.length > 0) {
            callback(acceptedFiles);
        }
        if (rejectedFiles.length > 0) {
            DefaultToaster.show({ message: "Wrong file type, Accoeting only mp3 and wav", className: "bp3-intent-danger" })
            console.log(rejectedFiles, event)
        }
    }
    const getWrappedDropzone = () => {
        const dropzoneContent = (props: DropzoneState) => (
            <section>
                <div {...props.getRootProps()}>
                    <input {...props.getInputProps()} />
                    <LanguageContext.Consumer>
                        {({ strings }) => <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>}
                    </LanguageContext.Consumer>
                </div>
            </section>
        )

        return (
            <Dropzone
                accept={['audio/mp3', 'audio/wav', 'audio/mpeg', 'audio/x-wav']}
                onDrop={getDefaultOnDrop}
                multiple={false}
                maxSize={30000000}
            >
                {dropzoneContent}
            </Dropzone>
        );
    }

    return getWrappedDropzone();
}

export default DropZoneWrapper;
