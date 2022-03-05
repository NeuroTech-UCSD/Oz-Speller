import React, { useEffect, useRef, useState } from 'react'
import './FlickerBox.css'

function FlickerBox(props) {
    const {text, freq, ops, fps, phase, ...rest} = props
    const [isOn, setIsOn] = useState(true);
    const [opacity, setOpacity] = useState(1);
    const [index, setIndex] = useState(0);
    const indxRef = useRef(index);
    indxRef.current = index;
    const eHT = 1/freq/2*1000
    // console.log("variables reset")
    const updateState = (cTime) => {
        // '''

        // :param f: frequency of a target
        // :param phi: phase of a target
        // :param i: frame index (0 - 59 if fps = 60)
        // :return: luminance level (0 - 1)
        // '''
        // return 1 / 2 * (1 + np.sin(2 * np.pi * f * (i / monitor_fps) + phi))
        // console.log(indxRef.current)

        const op = 1.0 / 2.0 * (1.0 + Math.sin(2 * Math.PI * freq * (indxRef.current / fps) + phase))
        setOpacity(op)
        // if (text === "A") {
        //     // console.log(index)
        //     // console.log(Math.sin(2 * Math.PI * freq * (index / fps)))
        // }

        const newInd = indxRef.current === fps - 1 ? 0 : indxRef.current + 1;
        // console.log(index)
        setIndex(index => newInd)
        // console.log(index)

        // const result = Math.floor(cTime / eHT)%2 === 0;
        // setIsOn(result)

        if (ops) {
            requestAnimationFrame(updateState)
        }
    }
    
    useEffect(() => {
        if (ops) {
            requestAnimationFrame(updateState)
        }
    }, [ops])

    return (
        // <div style={{ opacity: isOn ? 1 : 0 }} className="box">
        //     { text }
        // </div>
        <div style={{ opacity: opacity }} className="box">
            { text }
        </div>
    )
}

export default FlickerBox