import React, { Component } from 'react';

import { Button } from '@blueprintjs/core';

export class Generate extends Component<{}> {

  public render() {
    return (
      <div className="PqM-Generate">
        <div className="PqM-header">
          Generate music
          </div>
        <div>
          Magenra
        </div>
        <Button text="Generate"/>
      </div>
    );
  }

}

export default Generate;
