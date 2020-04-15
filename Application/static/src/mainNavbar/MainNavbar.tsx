import React, { Fragment } from 'react';

import { Navbar, Button, Alignment } from "@blueprintjs/core";
import { IconName } from "@blueprintjs/icons";
import { ViewState } from '../shared/enums';

import strings from '../shared/strings';

type MainNavbarProps = {
    OnViewStateChange: (viewState: ViewState) => void,
    CurremtViewState: ViewState
}

export const MainNavbar: React.FC<MainNavbarProps> = ({ OnViewStateChange, CurremtViewState }) => {
    type ViewButtonProps = {
        iconName: IconName,
        viewState: ViewState,
        text: string
    }
    const getViewButton = (viewButtonProps: ViewButtonProps) => {
        const className = viewButtonProps.viewState === CurremtViewState ? "bp3-minimal is-active" : "bp3-minimal";
        return (
            <Button
                className={className}
                icon={viewButtonProps.iconName}
                text={viewButtonProps.text}
                onClick={() => OnViewStateChange(viewButtonProps.viewState)}
            />
        )
    }
    const getViewButtons = () => {
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
    return (
        <Navbar className="PqM-main-navbar">
            <Navbar.Group align={Alignment.LEFT}>
                {getViewButtons()}
            </Navbar.Group>
        </Navbar>
    );
};