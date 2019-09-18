import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../../dataService/DataService';
import { Toast } from '@blueprintjs/core';


export const Spectogram: FC = () => {
    const dropzoneContent = (props: DropzoneState) => (
        <section>
            <div {...props.getRootProps()}>
                <input {...props.getInputProps()} />
                <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>
            </div>
        </section>
    )
    const handleChange = (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        //TODO: Blueprint toaster progress bar
        if (acceptedFiles.length > 0) {
            const response = DataService.SayHello(acceptedFiles[0])
            // if(response.error) {
            //     blueprint toaster show error
            // }
        }
        if (rejectedFiles.length > 0) {
            console.log(rejectedFiles, event)
        }
    }
    const content = (
        <div className="PqM-Utility_spectogram">
            <Dropzone
                accept='audio/mp3'
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
            label={strings.rowLabelSpectogram}
        />
    );
}

export default Spectogram;