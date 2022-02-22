import React, { useEffect, useState } from "react";
import FlickerBox from "../shared/FlickerBox";
import './FlashingPage.css';
import socketIOClient from "socket.io-client";

function FlashingPage() {
    const [ops, setOps] = useState(false);
    const [pred, setPred] = useState("");

    let socket = null;
    let config = null;

    useEffect(() => {
        socket = socketIOClient("http://localhost:4002");
        config = socket.call('frontend ready');
        
        // TODO: insert correct events into .on() for predicting and holding
        socket.on('start_flashing', (trial) => {
            setPred(trial);
            
            // call function to countdown in UI
            await new Promise(setTimeout(() => {
                socket.emit('countdown done', Date.now());
            }, config.countdown));
            
            setOps(true);

            await new Promise(setTimeout(() => {
                setOps(false);
                socket.emit('finished flashing');
            }, config.TRIAL_DURATION));

            // should get the prediction
        });
    });

    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    return (
        <>
        <h1 style={{textAlign: "center"}}>Trial: {pred}</h1>
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

export default FlashingPage;