import React, { Fragment } from 'react';

import { Navbar, Button, Alignment } from "@blueprintjs/core";
import { IconName } from "@blueprintjs/icons";
import { ViewState } from '../shared/enums';
import { IStrings, LanguageContext, languagesEnum } from '../shared/languageContext';
import logo from './logo.png';

type MainNavbarProps = {
    OnViewStateChange: (viewState: ViewState) => void,
    CurrentViewState: ViewState,
    OnChangeLanguage: (newLanguage: languagesEnum) => void
}

export const MainNavbar: React.FC<MainNavbarProps> = ({ OnViewStateChange, CurrentViewState, OnChangeLanguage }) => {
    type ViewButtonProps = {
        iconName: IconName,
        viewState: ViewState,
        text: string
    }
    const getViewButton = (viewButtonProps: ViewButtonProps) => {
        const className = viewButtonProps.viewState === CurrentViewState ? "bp3-minimal is-active" : "bp3-minimal";
        return (
            <Button
                className={className}
                icon={viewButtonProps.iconName}
                text={viewButtonProps.text}
                onClick={() => OnViewStateChange(viewButtonProps.viewState)}
            />
        )
    }
    const getViewButtons = (strings: IStrings) => {
        const homeButton = getViewButton({
            iconName: "home",
            text: strings.navBarHome,
            viewState: ViewState.home
        });
        const transcribeButton = getViewButton({
            iconName: "music",
            text: strings.navBarTranscribe,
            viewState: ViewState.transcribe
        });
        const utilityButton = getViewButton({
            iconName: "pulse",
            text: strings.navBarUtility,
            viewState: ViewState.utility
        });

        return (
            <Fragment>
                {homeButton}
                {transcribeButton}
                {utilityButton}
            </Fragment>
        );
    }
    const getLanguageChangeButtons = (currLanguage: languagesEnum) => {
        const getClassName = (language: languagesEnum) => language === currLanguage ? "bp3-minimal is-active" : "bp3-minimal";

        return (
            <>
                <Button
                    className={getClassName(languagesEnum.eng)}
                    text={"eng"}
                    onClick={() => OnChangeLanguage(languagesEnum.eng)}
                />
                <Button
                    className={getClassName(languagesEnum.pl)}
                    text={"pl"}
                    onClick={() => OnChangeLanguage(languagesEnum.pl)}
                />
            </>
        );
    }
    return (
        <LanguageContext.Consumer>
            {({strings, language}) => (
                <Navbar className="PqM-main-navbar">
                    <Navbar.Group align={Alignment.LEFT}>
                        <Navbar.Heading ><img src={logo} alt="PqMusic Logo" /></Navbar.Heading>
                        <Navbar.Divider />
                        {getViewButtons(strings)}
                    </Navbar.Group>
                    <Navbar.Group align={Alignment.RIGHT}>
                            {getLanguageChangeButtons(language)}
                    </Navbar.Group>
                </Navbar>
            )}
        </LanguageContext.Consumer>
    );
};