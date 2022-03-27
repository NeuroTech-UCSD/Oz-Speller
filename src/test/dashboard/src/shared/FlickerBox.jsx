import React, { useEffect, useRef, useState } from 'react'
import './FlickerBox.css'

function FlickerBox(props) {
    const {text, freq, ops, fps, phase, ...rest} = props
    const [opacity, setOpacity] = useState(1);
    const [index, setIndex] = useState(0);
    const indxRef = useRef(index);
    const mounted = useRef(false);
    indxRef.current = index;
    const updateState = (cTime) => {
        if (mounted) {
            // '''
    
            // :param f: frequency of a target
            // :param phi: phase of a target
            // :param i: frame index (0 - 59 if fps = 60)
            // :return: luminance level (0 - 1)
            // '''
            // 1 / 2 * (1 + np.sin(2 * np.pi * f * (i / monitor_fps) + phi))
    
            const op = 1.0 / 2.0 * (1.0 + Math.sin(2 * Math.PI * freq * (indxRef.current / fps) + phase))
            setOpacity(op)
    
            const newInd = indxRef.current === fps - 1 ? 0 : indxRef.current + 1;
            setIndex(index => newInd)
    
            requestAnimationFrame(updateState)
        }

    }
    
    useEffect(() => {
        mounted.current = true;

        if (ops) {
            requestAnimationFrame(updateState)
        }

        return () => mounted.current = false;
    }, [ops])

    return (
        <div style={{ opacity: opacity }} className="box">
            { text }
        </div>
    )
}

export default FlickerBox