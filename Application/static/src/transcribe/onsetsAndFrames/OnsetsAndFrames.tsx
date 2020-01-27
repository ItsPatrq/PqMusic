import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../../dataService/DataService';

export type OnsetsAndFramesProps = {

}

export const OnsetsAndFrames: FC<OnsetsAndFramesProps> = () => {

    const handleOnesetsAndFramesChange = (acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) => {
        if (acceptedFiles.length > 0) {
          DataService.TranscribeByOnsetsFrames(acceptedFiles[0])
        }
        if (rejectedFiles.length > 0) {
          console.log(rejectedFiles, event)
        }
      }
    const getOnesetsAndFramesContent = () => {
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
                onDrop={handleOnesetsAndFramesChange}
                multiple={false}
            >
                {dropzoneContent}
            </Dropzone>
        );
    }

    return (
        <RowFlex
            children={getOnesetsAndFramesContent()}
            label={strings.rowLabels.transcription.onesetsAndFrames}
        />
    );
}

export default OnsetsAndFrames;
