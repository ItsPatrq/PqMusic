import React, {Component} from 'react';

import { Home } from "../home/Home";
import { MainNavbar } from '../mainNavbar/MainNavbar';
import { ViewState } from '../shared/enums';
import { Transcribe } from '../transcribe/Transcribe';
import { Utility } from '../utility/Utility';
import getContextValue, { languagesEnum, LanguageContext } from '../shared/languageContext';
type AppState = {
  currentViewState: ViewState,
  language: languagesEnum
}

export class App extends Component<{}, AppState> {
  constructor(props: object) {
    super(props);
    this.state = {
      currentViewState: ViewState.home,
      language: languagesEnum.eng
    };
  }

  getContent = () => {
    return {
      [ViewState.home]: <Home />,
      [ViewState.transcribe]: <Transcribe />,
      [ViewState.utility]: <Utility />,
    }[this.state.currentViewState]
  }

  onViewStateChange = (newViewState: ViewState) => {
    this.setState({
      currentViewState: newViewState
    });
  }

  changeLanguage = (newLanguage: languagesEnum) => {
    if(newLanguage === this.state.language) {
      return;
    }
    this.setState({
      language: newLanguage
    });
  }

  public render() {
    return (
      <LanguageContext.Provider value={getContextValue(this.state.language)}>
        <div className="PqM">
          <header className="PqM-header">
            
            <MainNavbar OnChangeLanguage={this.changeLanguage} OnViewStateChange={this.onViewStateChange} CurrentViewState={this.state.currentViewState} />
          </header>

            {this.getContent()}
            
        </div>
      </LanguageContext.Provider>
    );
  }

}

export default App;
