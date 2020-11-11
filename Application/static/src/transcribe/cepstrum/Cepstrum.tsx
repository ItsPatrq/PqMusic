import React, { FC } from 'react';
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import DataService from '../../dataService/DataService';
import DropZoneWrapper from '../../shared/components/dropZoneWrapper/DropZoneWrapper';
import { ImageResult } from '../../shared/components/dialogWithResImages/DialogWithResImages';
import { IStrings, LanguageContext } from '../../shared/languageContext';

export const Cepstrum: FC<{ openDialog(res: ImageResult[]): void }> = ({ openDialog }) => {

    const getHandleFileInputChange = (strings: IStrings) =>  (acceptedFiles: File[]) => {
        DataService.TranscribeByCepstrum(acceptedFiles[0], (res) => { 
            const result:ImageResult[] = [{
                image: res.cepstrogram,
                title: strings.plots.cepstrogram
            }, {
                image: res.pitches,
                title: strings.plots.pitches
            }, {
                image: res.spectrogram,
                title: strings.plots.powerSpec
            }, {
                image: res.logSpectrogram,
                title: strings.plots.logPowSpec
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
                    label={strings.rowLabels.transcription.cepstrum}
                /> 
            )}
        </LanguageContext.Consumer>
    );
}

