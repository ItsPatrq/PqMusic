import React from 'react';

export type RowFlexProps = {
    label: string,
    children: React.ReactNode
}

export const RowFlex: React.FC<RowFlexProps> = ({label, children}) => {

    return (
        <div className="PqM-rows">
           <div className="PqM-row">
            <div className="PqM-row_label">
                <span>
                    {label + ":"}
                </span>
            </div>
            <div className="PqM-row_content">
                {children}
            </div>
           </div>
        </div>
    );
};