import React, { Component } from 'react';

import Dropzone, { DropEvent, DropzoneState } from 'react-dropzone';
import DataService from '../dataService/DataService';
import strings from '../shared/strings';
import { RowFlex } from '../shared/components/rowFlex/RowFlex';

export class Generate extends Component<{}> {
  handleUnconditionedTransform(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.GenerateUnconditionedTransform(acceptedFiles[0])
    }
    if (rejectedFiles.length > 0) {
      console.log(rejectedFiles, event)
    }
  }

  handleConditionedTransform(acceptedFiles: File[], rejectedFiles: File[], event: DropEvent) {
    if (acceptedFiles.length > 0) {
      DataService.GenerateConditionedTransform(acceptedFiles[0])
    }
    if (rejectedFiles.length > 0) {
      console.log(rejectedFiles, event)
    }
  }

  getUnconditionedTransform() {
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
          accept={['audio/midi']}
          onDrop={this.handleUnconditionedTransform}
          multiple={false}
      >
          {dropzoneContent}
      </Dropzone>
    );
  }

  getConditionedTransform() {
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
          accept={['audio/midi']}
          onDrop={this.handleConditionedTransform}
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
          children={this.getUnconditionedTransform()}
          label={strings.rowLabels.generate.unconditionedTransform}
        />
        <RowFlex
          children={this.getConditionedTransform()}
          label={strings.rowLabels.generate.melodyConditionedTransform}
        />
      </div>
    );
  }


}

export default Generate;
