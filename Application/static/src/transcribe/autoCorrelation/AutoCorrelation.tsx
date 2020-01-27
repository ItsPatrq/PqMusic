import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';

export const AutoCorrelation: FC<{}> = () => {


    const handleOnesetsAndFramesChange = (acceptedFiles: File[]) => {
        DataService.TranscribeByAutoCorrelation(acceptedFiles[0])
    }
    const getAutoCorrelationContent = () => {


        return (
            <DropZoneWrapper
                callback={handleOnesetsAndFramesChange}
                multiple={false}
            />
        );
    }

    return (
        <RowFlex
            children={getAutoCorrelationContent()}
            label={strings.rowLabels.transcription.autoCorrelation}
        />
    );
}

export default AutoCorrelation;
