import React, { Component } from 'react';

import { Button } from '@blueprintjs/core';
import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone'
import DataService from '../dataService/DataService';

export class Transcribe extends Component<{}> {
  handleChange(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.SayHello(acceptedFiles[0])
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
        <Dropzone
          accept='audio/mp3'
          onDrop={this.handleChange}
          multiple={false}
        >
          {x}
        </Dropzone>
        <br />
        <Button type="submit" className="bp3-intent-primary" text="Wyslij" />
      </div>
    );
  }

}

export default Transcribe;

const x = (props: DropzoneState) => (
  <section>
    <div {...props.getRootProps()}>
      <input {...props.getInputProps()} />
      <p>Drag or click to upload your exported composition</p>
    </div>
  </section>
)