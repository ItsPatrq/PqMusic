import React, { Component } from 'react';

import { Button } from '@blueprintjs/core';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../dataService/DataService';
import strings from '../shared/strings';

export class Transcribe extends Component<{}> {
  handleChange(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.Transcribe(acceptedFiles[0])
      //reader.readAsBinaryString(accepted[0]);
    }
    if (rejectedFiles.length > 0) {
      console.log(rejectedFiles, event)
    }
  }
  public render() {
    return (
      <div className="PqM-Transcribe">
        <div className="PqM-header">
          Transcribe
          </div>
        <div>
          Onsets and Frames
        </div>
        <Dropzone
          accept='audio/mp3'
          onDrop={this.handleChange}
          multiple={false}
        >
          {dropzoneContent}
        </Dropzone>
        <br />
        <Button type="submit" className="bp3-intent-primary" text="Wyslij" />
      </div>
    );
  }

}

export default Transcribe;

const dropzoneContent = (props: DropzoneState) => (
  <section>
    <div {...props.getRootProps()}>
      <input {...props.getInputProps()} />
      <p className="PqM-dropZone">{strings.dropZoneDefaultMessage}</p>
    </div>
  </section>
)