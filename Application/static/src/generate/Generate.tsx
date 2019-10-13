import React, { Component } from 'react';

import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone';
import DataService from '../dataService/DataService';
import strings from '../shared/strings';
import { RowFlex } from '../shared/components/rowFlex/RowFlex';

export class Generate extends Component<{}> {
  handleTransformChange(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.GenerateTransform()
    }
    if (rejectedFiles.length > 0) {
      console.log(rejectedFiles, event)
    }
  }

  getGenerateTransformContent() {
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
          onDrop={this.handleTransformChange}
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
          Generate
          </div>
        <RowFlex
          children={this.getGenerateTransformContent()}
          label={strings.rowLabels.generate.transform}
        />
      </div>
    );
  }


}

export default Generate;
