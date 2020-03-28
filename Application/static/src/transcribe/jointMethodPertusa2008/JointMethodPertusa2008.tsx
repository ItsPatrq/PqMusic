import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';

export const JointMethodPertusa2008: FC<{ }> = () => {

    const handleFileInputChange = (acceptedFiles: File[]) => {
        DataService.TranscribeByJointMethodPertusa2008(acceptedFiles[0]);
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
            label={strings.rowLabels.transcription.jointMethodPertusa2008}
        />
    );
}

