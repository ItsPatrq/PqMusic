import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';
import { IStrings, LanguageContext } from '../../shared/languageContext';

export const GenerativeMethodPertusa2008: FC<{ }> = () => {

    const getHandleFileInputChange = (strings: IStrings) => (acceptedFiles: File[]) => {
        DataService.TranscribeByGenerativeMethodPertusa2008(acceptedFiles[0], strings);
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
                    label={strings.rowLabels.transcription.GenerativeMethodPertusa2008}
                />
            )}
        </LanguageContext.Consumer>
    );
}

