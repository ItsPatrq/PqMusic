import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';

export const GenerativeMethodPertusa2012: FC<{}> = () => {

    const handleFileInputChange = (acceptedFiles: File[]) => {
        DataService.TranscribeByGenerativeMethodPertusa2012(acceptedFiles[0]);
    }
    const getRowContent = () => (
        <DropZoneWrapper
            callback={handleFileInputChange}
            multiple={false}
        />
    );

    return (
        <RowFlex
            children={getRowContent()}
            label={strings.rowLabels.transcription.GenerativeMethodPertusa2012}
        />
    );
}

