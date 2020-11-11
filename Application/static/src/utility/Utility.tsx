import React, {Component} from 'react';
import { LanguageContext } from '../shared/languageContext';
import { FqMidi } from './FqMidi/FqMidi';
import Spectrogram from './Spectrogram/Spectrogram';
export type UtilityState = {
  fqMidiValue: number
}

const utilityDefaultState: UtilityState = {
  fqMidiValue: 440
};

export class Utility extends Component<{}, UtilityState> {
  constructor(props: any){
    super(props);
    this.state = utilityDefaultState;
  }
  handleFqMidiValueChange = (value: number) => {
    this.setState(() => {
       return {
         fqMidiValue: value
       }
    });
  }
  countFqMidiValueChange = () => {
    return (69 + (12 * Math.log2(this.state.fqMidiValue / 440))).toFixed(4);
  }
  public render = () => {
    return (
      <LanguageContext.Consumer>
        {({strings}) => (
          <div className="PqM-Utility">
            <div className="PqM-header">
              {strings.titleUtilities}
            </div>

            <FqMidi 
              fqMidiValue={this.state.fqMidiValue} 
              handleFqMidiValueChange={this.handleFqMidiValueChange}
            />
            <Spectrogram />
            {/* {process.env.REACT_APP_ENV === "local" &&  < WindowFunctions /> } */}
            
            
          </div>
        )}
      </LanguageContext.Consumer>
    );
  }

}

export default Utility;
