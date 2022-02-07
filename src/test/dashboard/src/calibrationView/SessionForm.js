import React from "react";

const SessionForm = () => {
    return (
        <form style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
            <label>Subject Name:
                <input 
                    type="text" 
                    name="subject_name"
                />
            </label>
            <label>Session Number:
                <input 
                    type="number" 
                    name="session_number" 
                    value={0}
                />
            </label>
            <label>Startup Delay:
                <input 
                    type="number" 
                    name="startup_delay" 
                    value={0}
                />
            </label>
            <label>Trial Duration:
                <input 
                    type="number" 
                    name="trial_duration" 
                    value={2000}
                />
            </label>
            <label>Inter-trial Interval:
                <input 
                    type="number" 
                    name="inter_trial_interval" 
                    value={1000}
                />
            </label>
            <label>Number of Trials:
                <input 
                    type="number" 
                    name="num_trials" 
                    value={7}
                />
            </label>
            <label>Number of Target Frequencies:
                <input 
                    type="number" 
                    name="num_target_frequencies" 
                />
            </label>
            <label>Channels:
                <input 
                    type="text" 
                    name="channels" 
                />
            </label>
            <input type="submit" />
        </form>
    );
}

export default SessionForm;