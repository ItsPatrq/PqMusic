import React, { Component } from 'react';
import AutoCorrelation from './autoCorrelation/AutoCorrelation';
import strings from '../shared/strings';
import { DialogWithResImages, ImageResult } from '../shared/components/dialogWithResImages/DialogWithResImages';

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
          <AutoCorrelation 
            openDialog={(res) => this.openDialog(res, "Auto Correlation")}
          />
      </div>
    );
  }

}

export default Transcribe;

