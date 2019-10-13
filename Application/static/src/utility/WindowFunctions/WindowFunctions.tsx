import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import DataService from '../../dataService/DataService';
import { Button } from '@blueprintjs/core';


export const WindowFunctions: FC = () => {
    const handleHannOnClickEvent = () => {
        DataService.HannWindow();
    };
    const handleHammingOnClickEvent = () => {
        DataService.HammingWindow();
    };
    const handleRectangleOnClickEvent = () => {
        DataService.RectangleWindow();
    };
    const content = (
        <div className="PqM-Utility_window_functions">
            <Button
                className="bp3-intent-primary"
                onClick={handleHannOnClickEvent}
                text={strings.buttonLabelDownloadHannWindow}
            />
            <Button
                className="bp3-intent-primary"
                onClick={handleHammingOnClickEvent}
                text={strings.buttonLabelDownloadHammingWindow}
            />
            <Button
                className="bp3-intent-primary"
                onClick={handleRectangleOnClickEvent}
                text={strings.buttonLabelDownloadRectangleWindow}
            />
        </div>
    )

    return (
        <RowFlex
            children={content}
            label={strings.rowLabels.utils.windowFunctions}
        />
    );
}

export default WindowFunctions;