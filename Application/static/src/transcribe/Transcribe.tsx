import React, {Component} from 'react';

import { FileInput, Button } from '@blueprintjs/core';

export class Transcribe extends Component<{}> {
  public render() {
    return (
        <div className="PqM-Transcribe">
            <div className="PqM-header">
                Transcribe
            </div>
            <FileInput onInputChange={(x) => console.log(x)}/>
            <br/>
            <Button type="submit" className="bp3-intent-primary" text="Wyslij" />
        </div>
    );
  }

}

export default Transcribe;
