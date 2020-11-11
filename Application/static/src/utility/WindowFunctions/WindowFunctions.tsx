import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import DataService from '../../dataService/DataService';
import { Button } from '@blueprintjs/core';
import { IStrings, LanguageContext } from '../../shared/languageContext';


export const WindowFunctions: FC = () => {
    const getHandleHannOnClickEvent = (strings: IStrings) => () => {
        DataService.HannWindow(strings);
    };
    const getHandleHammingOnClickEvent = (strings: IStrings) => () => {
        DataService.HammingWindow(strings);
    };
    const getHandleRectangleOnClickEvent = (strings: IStrings) => () => {
        DataService.RectangleWindow(strings);
    };
    const getContent = (strings: IStrings) => (
        <div className="PqM-Utility_window_functions">
            <Button
                className="bp3-intent-primary"
                onClick={getHandleHannOnClickEvent(strings)}
                text={strings.buttonLabelDownloadHannWindow}
            />
            <Button
                className="bp3-intent-primary"
                onClick={getHandleHammingOnClickEvent(strings)}
                text={strings.buttonLabelDownloadHammingWindow}
            />
            <Button
                className="bp3-intent-primary"
                onClick={getHandleRectangleOnClickEvent(strings)}
                text={strings.buttonLabelDownloadRectangleWindow}
            />
        </div>
    )

    return (
        <LanguageContext.Consumer>
            {({strings}) => (
                <RowFlex
                    children={getContent(strings)}
                    label={strings.rowLabels.utils.windowFunctions}
                />
            )}
        </LanguageContext.Consumer>
    );
}

export default WindowFunctions;