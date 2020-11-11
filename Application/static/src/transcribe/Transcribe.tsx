import React, { Component } from 'react';
import { AutoCorrelation } from './autoCorrelation/AutoCorrelation';
import { DialogWithResImages, ImageResult } from '../shared/components/dialogWithResImages/DialogWithResImages';
import { Cepstrum } from './cepstrum/Cepstrum';
import { Aclos } from './aclos/Aclos';
import { GenerativeMethodPertusa2008 } from './generativeMethodPertusa2008/GenerativeMethodPertusa2008';
import { GenerativeMethodPertusa2012 } from './generativeMethodPertusa2012/GenerativeMethodPertusa2012';
import { OnsetsAndFrames } from './onsetsAndFrames/OnsetsAndFrames';
import { LanguageContext } from '../shared/languageContext';


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
      <LanguageContext.Consumer>
        {({strings}) => (
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
              <GenerativeMethodPertusa2008  />
              <GenerativeMethodPertusa2012 />
              <OnsetsAndFrames />
          </div>
        )}
      </LanguageContext.Consumer>
    );
  }

}

export default Transcribe;

