import React from 'react';
import { LanguageContext } from '../shared/languageContext';

export const Home: React.FC = () => {
    return (
        <LanguageContext.Consumer>
            {({strings}) => (
            <div className="PqM-home PqM-header">
                {strings.homePage}
            </div>
            )}
        </LanguageContext.Consumer>
    );
};