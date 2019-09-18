import React, { FC } from 'react';
import { NumericInput } from "@blueprintjs/core";
import { RowFlex } from '../../shared/components/rowFlex/RowFlex';
import strings from '../../shared/strings';

export type FqMidiProps = {
  fqMidiValue: number,
  handleFqMidiValueChange: (value: number) => void
}

export const FqMidi: FC<FqMidiProps> = ({fqMidiValue, handleFqMidiValueChange}) => {

    const countFqMidiValueChange = () => {
        return (69 + (12 * Math.log2(fqMidiValue / 440))).toFixed(4);
    };

    const content = (
        <div className="PqM-Utility_fqMidi">
            <div className="PqM-Utility_fqMidi_result">{countFqMidiValueChange()}</div> = 69 + 12 * log2(f / 440); <div className="PqM-Utility_fqMidi_variable">f</div> =
            <NumericInput
                allowNumericCharactersOnly={true}
                onValueChange={handleFqMidiValueChange}
                value={fqMidiValue}
            />
        </div>
    )

    return (
        <RowFlex
            children={content}
            label={strings.rowLabelFqMIDI}
        />
    );
}

export default FqMidi;
