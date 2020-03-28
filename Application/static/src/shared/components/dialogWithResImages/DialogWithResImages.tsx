import React, { FC, ReactElement } from 'react';
import Carousel from '@brainhubeu/react-carousel';
import '@brainhubeu/react-carousel/lib/style.css';

import { Button, Classes, Dialog, Tooltip } from "@blueprintjs/core";

export interface DialogWithResImagesProps {
    onclose(): void;
    isOpen: boolean;
    results: ImageResult[];
    title: string;
}

export interface ImageResult {
    title: string,
    image: string,
}
export const DialogWithResImages: FC<DialogWithResImagesProps> = ({ onclose, title, isOpen = false, results = []}) => {
    const images:ReactElement[] = [];
    results.forEach(res => {
        images.push(<img src={`data:image/png;base64,${res.image}`} key={res.title} alt={res.title} />)
    });
    return (
        <Dialog
            icon="info-sign"
            className="PqM-dialog with-res-images"
            onClose={onclose}
            autoFocus={true}
            title={title}
            canEscapeKeyClose={true}
            canOutsideClickClose={false}
            enforceFocus={true}
            isOpen={isOpen}
        >
            <div className={Classes.DIALOG_BODY}>
                <Carousel
                    arrows dots
                >
                    {images}
                </Carousel>
            </div>
            <div className={Classes.DIALOG_FOOTER}>
                <div className={Classes.DIALOG_FOOTER_ACTIONS}>
                    <Tooltip content="Close the dialog.">
                        <Button onClick={onclose}>Close</Button>
                    </Tooltip>
                </div>
            </div>
        </Dialog>
    );
}
