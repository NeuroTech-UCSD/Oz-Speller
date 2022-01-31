import React from 'react';
import { Snackbar } from '@material-ui/core';
import MuiAlert from '@material-ui/lab/Alert';

function CustomSnackbar({ children, setOpen, open, severity }) {
    const onClose = (_, reason) => reason === 'clickaway' || setOpen(false);

    return <Snackbar open={open} autoHideDuration={6000} onClose={onClose}>
        <MuiAlert elevation={6} variant="filled" onClose={onClose} severity={severity}>
            {children}
        </MuiAlert>
    </Snackbar>;
}

export function EnterIdSnackbar(props) {
    return <CustomSnackbar {...props} severity="error">
        You must enter a subject ID to record data.
    </CustomSnackbar>;
};

export function EnterPromptSnackbar(props) {
    return <CustomSnackbar {...props} severity="error">
        {props.mode === 2 && <>You must enter custom prompts to use the In the Air mode.</>}
        {props.mode === 3 && <>You must enter text to use the Touch-Type mode.</>}
    </CustomSnackbar>
};

export function RecordingStoppedSnackbar(props) {
    return <CustomSnackbar {...props} severity="info">
        Recording stopped!
    </CustomSnackbar>;
};