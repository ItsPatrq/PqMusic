import React, { Component } from 'react';

import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../dataService/DataService';
import strings from '../shared/strings';
import { RowFlex } from '../shared/components/rowFlex/RowFlex';

export class Transcribe extends Component<{}> {
  handleOnesetsAndFramesChange(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.TranscribeByOnsetsFrames(acceptedFiles[0])
    }
    if (rejectedFiles.length > 0) {
      console.log(rejectedFiles, event)
    }
  }

  getOnesetsAndFramesContent() {
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
          onDrop={this.handleOnesetsAndFramesChange}
          multiple={false}
      >
          {dropzoneContent}
      </Dropzone>
    );
  }

  public render() {
    return (
      <div className="PqM-Transcribe">
        <div className="PqM-header">
          Transcribe
          </div>
        <RowFlex
          children={this.getOnesetsAndFramesContent()}
          label={strings.rowLabels.transcription.onesetsAndFrames}
        />
      </div>
    );
  }

}

export default Transcribe;

