import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';
import { ImageResult } from '../../shared/components/dialogWithResImages/DialogWithResImages';

export const AutoCorrelation: FC<{ openDialog(res: ImageResult[]): void }> = ({ openDialog }) => {

    const handleFileInputChange = (acceptedFiles: File[]) => {
        DataService.TranscribeByAutoCorrelation(acceptedFiles[0], (res) => { 
            const result:ImageResult[] = [{
                image: res.correlogram,
                title: "correlogram"
            }, {
                image: res.pitches,
                title: "pitches"
            }]
            openDialog(result);
        });
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
            label={strings.rowLabels.transcription.autoCorrelation}
        />
    );
}