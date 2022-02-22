import React, { useEffect, useState } from "react";
import socketIOClient from "socket.io-client";
import FlickerBox from "./FlickerBox";
import './CalibrationPage.css';

function FlashingView(props) {
    const [state, setState] = useState(0)
    const [trial, setTrial] = useState(null)
    const sessionForm = props.config;

    const DEFAULT_FREQUENCY = 20;
    // let socket = null;

    useEffect(() => {
        // socket = socketIOClient("http://localhost:4002");
        // socket.emit('frontend-ready');
    })

    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return (
            <>
            {
                state === 0 ?
                <h1 style={{textAlign: "center"}}>Trial: {trial}</h1>
                :
                <h1 style={{textAlign: "center"}}>Upcoming Trial: {trial}</h1>
            }
            <div className="FlashingComponent">
            {
                [...characters].map((el, index) => 
                <FlickerBox 
                text={el}
                freq={sessionForm["TARGET_FREQUENCIES"][el.toLowerCase()] ? sessionForm["TARGET_FREQUENCIES"][el.toLowerCase()] : DEFAULT_FREQUENCY}
                ops={state === 3}
                key={index}
                />
                )
            }
            </div>
            </>
        )


}

export default FlashingView;