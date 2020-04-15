import React from 'react';
import DataService from '../dataService/DataService';
import strings from '../shared/strings';

export const Home: React.FC = () => {

    return (
        <div className="PqM-home PqM-header">
           <object data={DataService.GetThesisPaper()}>
               {strings.pdfObjectFallback}
           </object>
        </div>
    );
};