import React, { Component } from 'react';
import AutoCorrelation from './autoCorrelation/AutoCorrelation';
import strings from '../shared/strings';

export class Transcribe extends Component<{}> {
  public render() {
    return (
      <div className="PqM-Transcribe">
        <div className="PqM-header">
          {strings.titleTranscribe}
        </div>
          <AutoCorrelation />
      </div>
    );
  }

}

export default Transcribe;

