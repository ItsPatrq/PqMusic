import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';
import { ImageResult } from '../../shared/components/dialogWithResImages/DialogWithResImages';
import { IStrings, LanguageContext } from '../../shared/languageContext';

export const Aclos: FC<{ openDialog(res: ImageResult[]): void }> = ({ openDialog }) => {

    const getHandleFileInputChange = (strings: IStrings) => (acceptedFiles: File[]) => {
        DataService.TranscribeByAclos(acceptedFiles[0], (res) => { 
            const result:ImageResult[] = [{
                image: res.correlogram,
                title: strings.plots.correlogram
            }, {
                image: res.pitches,
                title: strings.plots.pitches
            }, {
                image: res.spectrogram,
                title: strings.plots.powerSpec
            }]
            openDialog(result);
        }, strings);
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
                    label={strings.rowLabels.transcription.aclos}
                />
            )}
        </LanguageContext.Consumer>
    );
}

