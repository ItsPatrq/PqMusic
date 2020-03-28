import React from 'react';
import DataService from '../dataService/DataService';

export const Home: React.FC = () => {

    return (
        <div className="PqM-home PqM-header">
           <object data={DataService.GetThesisPaper()}></object>
        </div>
    );
};