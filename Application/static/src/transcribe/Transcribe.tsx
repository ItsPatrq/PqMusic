import React, { Component } from 'react';
import { AutoCorrelation } from './autoCorrelation/AutoCorrelation';
import strings from '../shared/strings';
import { DialogWithResImages, ImageResult } from '../shared/components/dialogWithResImages/DialogWithResImages';
import { Cepstrum } from './cepstrum/Cepstrum';
import { Aclos } from './aclos/Aclos';
import { JointMethodPertusa2008 } from './jointMethodPertusa2008/JointMethodPertusa2008';
import { JointMethodPertusa2012 } from './jointMethodPertusa2012/JointMethodPertusa2012';
import { OnsetsAndFrames } from './onsetsAndFrames/OnsetsAndFrames';


interface ITranscribe {
  isResultDialogVisible: boolean
  handleResultDialogClose(): void;
  mostRecentResults: ImageResult[];
  mostRecentTitle: string;
}

export class Transcribe extends Component<{}, ITranscribe> {
  public state: ITranscribe = {
    isResultDialogVisible: false,
    handleResultDialogClose: () => this.setState({ isResultDialogVisible: false }),
    mostRecentResults: [],
    mostRecentTitle: ""
  }
  public openDialog = (res: ImageResult[], title: string) => {
    this.setState({ isResultDialogVisible: true, mostRecentResults: res, mostRecentTitle: title });
  }
  public render() {
    return (
      <div className="PqM-Transcribe">
        <DialogWithResImages 
          isOpen={this.state.isResultDialogVisible}
          onclose={this.state.handleResultDialogClose}
          results={this.state.mostRecentResults}
          title={this.state.mostRecentTitle}
        />
        <div className="PqM-header">
          {strings.titleTranscribe}
        </div>
        <h3>{strings.subTitleMonophonic}</h3>
          <AutoCorrelation 
            openDialog={(res) => this.openDialog(res, strings.modalLabels.transcription.autoCorrelationResult)}
          />
          <Cepstrum 
            openDialog={(res) => this.openDialog(res, strings.modalLabels.transcription.cepstrumResult)}
          />
          <Aclos 
            openDialog={(res) => this.openDialog(res, strings.modalLabels.transcription.aclosResult)}
          />
        <h3>{strings.subTitlePolyphonic}</h3>
          <JointMethodPertusa2008  />
          <JointMethodPertusa2012 />
          <OnsetsAndFrames />
      </div>
    );
  }

}

export default Transcribe;

