import React, { FC } from 'react';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import strings from '../../strings';

export type DropZoneWrapperProps = {
    callback(files:File[]):any,
    multiple:boolean
}

export const DropZoneWrapper: FC<DropZoneWrapperProps> = ({ callback, multiple = false }) => {

    const getDefaultOnDrop = (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        if (acceptedFiles.length > 0) {
            callback(acceptedFiles);
        }
        if (rejectedFiles.length > 0) {
          console.log(rejectedFiles, event)
        }
      }
    const getWrappedDropzone = () => {
        const dropzoneContent = (props: DropzoneState) => (
            <section>
                <div {...props.getRootProps()}>
                    <input {...props.getInputProps()} />
                    <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>
                </div>
            </section>
        )

        return (
            <Dropzone
                accept={['audio/mp3', 'audio/wav']}
                onDrop={getDefaultOnDrop}
                multiple={false}
            >
                {dropzoneContent}
            </Dropzone>
        );
    }

    return getWrappedDropzone();
}

export default DropZoneWrapper;
