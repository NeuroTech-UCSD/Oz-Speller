import React from "react";

const Navigation = ({changeRoute}) => {
    return (
        <nav style={{display: 'flex', justifyContent: 'flex-end'}}>
            <p onClick={() => changeRoute('calibration')}> Calibration </p>
            <p onClick={() => changeRoute('onlinePrediction')}> Online Prediction </p>
            <p onClick={() => changeRoute('plots')}> Plots </p>
        </nav>
    );
}

export default Navigation;