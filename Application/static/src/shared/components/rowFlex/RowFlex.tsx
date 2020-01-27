import React from 'react';

export type RowFlexProps = {
    label: string,
    children: React.ReactNode
}

export const RowFlex: React.FC<RowFlexProps> = ({label, children}) => {

    return (
        <div className="PqM-row-wrapper">
           <div className="PqM-row">
            <div className="PqM-row_label">
                <span>
                    {`${label}:`}
                </span>
            </div>
            <div className="PqM-row_content">
                {children}
            </div>
           </div>
        </div>
    );
};