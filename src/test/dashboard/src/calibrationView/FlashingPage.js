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
        config = socket.emit('frontend ready');
        
        // TODO: insert correct events into .on() for predicting and holding
        socket.on('start_flashing', (trial) => {
            setPred(trial);
            
            // call function to countdown in UI
            setTimeout(() => {
                socket.emit('countdown done', trial);
                var now = new Date();
                console.log("finished countdown:" + now.getMinutes() + ":" + now.getSeconds());
            }, config.INTER_TRIAL_INTERVAL);
            
            setOps(true);

            setTimeout(() => {
                setOps(false);
                socket.emit('finished flashing', "*");  // * is used as the null character
                var now = new Date();
                console.log("finished flashing:" + now.getMinutes() + ":" + now.getSeconds());
            }, config.TRIAL_DURATION);

            // should get the prediction
        });
    }, []);

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
            fps={60}
            key={index}
            />
            )
        }
        </div>
        </>
    )
}

export default FlashingPage;