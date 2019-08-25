import React, {Component} from 'react';
import './App.css';

import { Home } from "../home/Home";
import { MainNavbar } from '../mainNavbar/MainNavbar';
import { ViewState } from '../shared/enums';
import { Transcribe } from '../transcribe/Transcribe';
import { UploadMidi } from '../uploadMidi/UploadMidi';
import { Utility } from '../utility/Utility';
type AppState = {
  currentViewState: ViewState
}

export class App extends Component<{}, AppState> {
  constructor(props: object) {
    super(props);
    this.state = {
      currentViewState: ViewState.home
    };
  }

  getContent = () => {
    return {
      [ViewState.home]: <Home />,
      [ViewState.uploadMidi]: <UploadMidi />,
      [ViewState.transcribe]: <Transcribe />,
      [ViewState.utility]: <Utility />
    }[this.state.currentViewState]
  }

  onViewStateChange = (newViewState: ViewState) => {
    this.setState({
      currentViewState: newViewState
    });
  }

  public render() {
    return (
      <div className="App">
        <header className="App-header">
          
          <MainNavbar OnViewStateChange={this.onViewStateChange} CurremtViewState={this.state.currentViewState} />
        </header>

          {this.getContent()}
          
      </div>
    );
  }

}

export default App;
