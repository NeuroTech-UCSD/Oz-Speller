import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
    container: {
        backgroundColor: '#f1f1f1f1',
    },
    progress: {
        backgroundColor: '#9e9e9e',
    }
});

function ProgressBar({ percent }) {
    const classes = useStyles();

    return (
        <div className={classes.container}>
            <div className={classes.progress} style={{
                height: 24,
                width: percent + '%',
            }} />
        </div>
    );
}

export default ProgressBar;