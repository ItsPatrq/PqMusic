import React, { Fragment } from 'react';
import './MainNavBar.css';

import { Navbar, Button, Alignment } from "@blueprintjs/core";
import { IconName } from "@blueprintjs/icons";
import { ViewState } from '../shared/enums';

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
    const getViewButton = (viewButtonProps:ViewButtonProps) => {
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
            text: "Home",
            viewState: ViewState.home
        });
        const uploadMidiButton = getViewButton({
            iconName: "document",
            text: "Upload MIDI",
            viewState: ViewState.uploadMidi
        });
        const transcribeButton = getViewButton({
            iconName: "music",
            text: "Transcribe",
            viewState: ViewState.transcribe
        });

        return (
            <Fragment>
                {homeButton}
                {uploadMidiButton}
                {transcribeButton}
            </Fragment>
        );
    }
    return (
        <Navbar className="PqM-main-navbar">
            <Navbar.Group align={Alignment.LEFT}>
                <Navbar.Heading>PqMusic</Navbar.Heading>
                <Navbar.Divider />
                {getViewButtons()}
            </Navbar.Group>
        </Navbar>
    );
};