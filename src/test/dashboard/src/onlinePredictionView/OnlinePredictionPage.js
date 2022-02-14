import React, { useEffect, useState } from "react";
import FlickerBox from "../shared/FlickerBox";
import './OnlinePredictionPage.css';
import socketIOClient from "socket.io-client";

function OnlinePredictionPage() {
    const [ops, setOps] = useState(false);
    const [pred, setPred] = useState("")

    let socket = null;
    let config = null;

    useEffect(() => {
        socket = socketIOClient("http://localhost:4002");
        config = socket.call('frontend-ready');
        
        // TODO: insert correct events into .on() for predicting and holding
        socket.on('generate trial', (trial) => {
            setPred(trial)
            setTimeout(() => {
                // do countdown on ui
                socket.emit('countdown done')
            }, config.interval)
            setOps(true)
            setTimeout(() => {
                // do countdown on ui
                setOps(false)
                socket.emit('finished flashing')
            }, config.inter_interval)

            // should get the prediction
        })

    })

    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return (
        <>
        <h1 style={{textAlign: "center"}}>Prediction: {pred}</h1>
        <div className="FlashingComponent">
        {
            [...characters].map((el, index) => 
            <FlickerBox 
            text={el}
            freq={index + 1}
            ops={ops}
            key={index}
            />
            )
        }
        </div>
        </>
    )
}

export default OnlinePredictionPage;