import React, { useEffect, useState } from "react";
import FlickerBox from "../shared/FlickerBox";
import './FlashingPage.css';
import socketIOClient from "socket.io-client";

function FlashingPage() {
    const [pred, setPred] = useState("");

    let socket = null;

    useEffect(() => {
        socket = socketIOClient("http://localhost:4002");
        socket.emit('frontend ready');
        
        socket.on('start_flashing', (trial) => {
            let curr = new Date();
            console.log("start flashing:", curr.getMinutes() + ":" + curr.getSeconds() + "." + curr.getMilliseconds())

            setPred(trial);
        });

        socket.on('stop_flashing', () => {
            let curr = new Date();
            console.log("stop flashing:", curr.getMinutes() + ":" + curr.getSeconds() + "." + curr.getMilliseconds())

            setPred("");
        })
    }, []);
    // "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const phase = 0.2415;
    return (
        <>
        <h1 style={{textAlign: "center"}}>Trial: {pred}</h1>
        <div className="FlashingComponent">
        {
            pred === "" ?
            
            [...characters].map((el, index) => 
            <div key={index} className="box">
            { el }
            </div>
            )

            :
            
            [...characters].map((el, index) => 
            <FlickerBox 
            text={el}
            freq={index + 1}
            ops={true}
            fps={60}
            phase={index * phase}
            key={index}
            />
            )
        }
        </div>
        </>
    )
}

export default FlashingPage;

            // console.log("BEFORE", before.getSeconds(), before.getMilliseconds())

            // console.log("AFTER", after.getSeconds(), after.getMilliseconds())
            // perform trial
            // setTimeout(() => {
            //     var now = new Date();
            //     console.log("finished countdown:" + now.getMinutes() + ":" + now.getSeconds() + "." + now.getMilliseconds());

            //     setOps(true);

            // }, config["INTER_TRIAL_INTERVAL"]);
            
            // setTimeout(() => {
            //     setOps(false);
            //     socket.emit('finished flashing', "*");  // * is used as the null character
            //     var now = new Date();
            //     console.log("finished flashing:" + now.getMinutes() + ":" + now.getSeconds() + "." + now.getMilliseconds());
            // }, config["TRIAL_DURATION"]);