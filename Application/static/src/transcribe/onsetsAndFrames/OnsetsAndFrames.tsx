import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';
import { IStrings, LanguageContext } from '../../shared/languageContext';

export const OnsetsAndFrames: FC<{}> = () => {

    const getHandleFileInputChange = (strings: IStrings) => (acceptedFiles: File[]) => {
        DataService.TranscribeByOnsetsFrames(acceptedFiles[0], strings);
    }
    const getRowContent = (strings: IStrings) => (
        <DropZoneWrapper
            callback={getHandleFileInputChange(strings)}
            multiple={false}
        />
    );

    return (
        <LanguageContext.Consumer>
            {({strings}) => (
                <RowFlex
                    children={getRowContent(strings)}
                    label={strings.rowLabels.transcription.onsetsAndFrames}
                />
            )}
        </LanguageContext.Consumer>
    );
}

