import React, {Component} from 'react';
import { NumericInput } from "@blueprintjs/core";

import './Utility.css';

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
      <div className="PqM-Utility">

        <div className="PqM-header">
            Utility
        </div>

        <div className="PqM-Utility_fqMidi">
          <div className="PqM-Utility_fqMidi_result">{this.countFqMidiValueChange()}</div> = 69 + 12 * log2(f / 440); <div className="PqM-Utility_fqMidi_variable">f</div> = 
          <NumericInput 
            onValueChange={this.handleFqMidiValueChange}
            value={this.state.fqMidiValue}
          />
        </div>
      </div>
    );
  }

}

export default Utility;
