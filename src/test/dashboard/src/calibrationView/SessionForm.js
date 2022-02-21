import React, { Component } from "react";
import socketIOClient from "socket.io-client";
import default_config from "./default_config.json"

class SessionForm extends Component {
    constructor(props) {
        super(props)
        this.socket = null;
        this.config = default_config;
    }

    componentDidMount() {
        const socket = socketIOClient("http://localhost:4002");
        this.socket = socket;
    }

    handleClick = () => {
        this.socket.emit('form submitted', this.config);
        this.props.changePage(1)
    }

    handleChange = (event) => {
        const config_key = event.target.name
        try {
            this.config[config_key] = (config_key === 'TARGET_FREQUENCIES') ? JSON.parse(event.target.value) :
                                    (config_key === 'CHANNELS') ? event.target.value.split(", ") :
                                    event.target.value;
        } catch (error) {
            ;
        }
    }
    
    render() {
        return (
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                <label>Subject Name:
                    <input 
                        type="text" 
                        name="SUBJECT_NAME"
                        onChange={this.handleChange}
                    />
                </label>
                <label>Session Number:
                    <input 
                        type="number" 
                        name="SESSION_NUMBER" 
                        defaultValue={this.config.SESSION_NUMBER}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Startup Delay:
                    <input 
                        type="number" 
                        name="STARTUP_DELAY" 
                        defaultValue={this.config.STARTUP_DELAY}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Trial Duration:
                    <input 
                        type="number" 
                        name="TRIAL_DURATION" 
                        defaultValue={this.config.TRIAL_DURATION}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Inter-trial Interval:
                    <input 
                        type="number" 
                        name="INTER_TRIAL_INTERVAL" 
                        defaultValue={this.config.INTER_TRIAL_INTERVAL}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Number of Trials:
                    <input 
                        type="number" 
                        name="NUM_TRIALS" 
                        defaultValue={this.config.NUM_TRIALS}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Target Frequencies (cannot parse single quotes):
                    <input 
                        type="text" 
                        name="TARGET_FREQUENCIES" 
                        defaultValue={JSON.stringify(this.config.TARGET_FREQUENCIES)}
                        onChange={this.handleChange}
                    />
                </label>
                <label>Channels:
                    <input 
                        type="text" 
                        name="CHANNELS" 
                        defaultValue={this.config.CHANNELS.toString()}
                        onChange={this.handleChange}
                    />
                </label>
                <button onClick={() => this.handleClick()} > Submit </button>
            </div>
        );
    }
}

export default SessionForm;