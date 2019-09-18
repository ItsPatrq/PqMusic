import React, {Component} from 'react';
import { FqMidi } from './FqMidi/FqMidi';
import Spectogram from './Spectogram/Spectogram';
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

        <FqMidi 
          fqMidiValue={this.state.fqMidiValue} 
          handleFqMidiValueChange={this.handleFqMidiValueChange}
        />
        <Spectogram 
          fqMidiValue={this.state.fqMidiValue} 
          handleFqMidiValueChange={this.handleFqMidiValueChange}
        />
        
        
      </div>
    );
  }

}

export default Utility;
