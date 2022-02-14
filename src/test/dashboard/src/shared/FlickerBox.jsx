import React, { useEffect, useState } from 'react'
import './FlickerBox.css'

function FlickerBox(props) {
    const {text, freq, ops, ...rest} = props

    const [isOn, setIsOn] = useState(true);
    const eHT = 1/freq/2*1000

    const updateState = (cTime) => {
        const result = Math.floor(cTime / eHT)%2 === 0;
        setIsOn(result)

        if (ops) {
            global.requestAnimationFrame(updateState)
        }
    }
    
    useEffect(() => {
        if (ops) {
            global.requestAnimationFrame(updateState)
        }
    })

    return (
        <div style={{ opacity: isOn ? 1 : 0}} className="box">
            { text }
        </div>
    )
}

export default FlickerBox