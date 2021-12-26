import React, { Component } from "react";
import Chart from 'react-apexcharts';
import ApexCharts from 'apexcharts';
import socketIOClient from "socket.io-client";

class Heatmap extends Component {
    constructor(props) {
        super(props);

        let fingerLabels = [
            'Nothing',
            'Right Thumb',
            'Right Index',
            'Right Middle',
            'Right Ring',
            'Right Pinky',
            'Left Index',
            'Left Middle',
            'Left Ring',
            'Left Pinky'
        ];

        let zeroData = [...Array(fingerLabels.length)].map((_, i) => ({ x: i + 1, y: 0, }));
        let series = fingerLabels.reduce((acc, curr) => [...acc, { name: curr, data: zeroData.slice(), }], []);

        this.state = {
            buffer: 0,
            counter: props.blockWidth + 1,
            series: series,
            options: {
                chart: {
                    id: 'heatmap',
                    height: 350,
                    type: 'heatmap',
                    animations: {
                        enabled: false,
                        dynamicAnimation: {
                            enabled: false
                        }
                    }
                },
                dataLabels: {
                    enabled: false
                },
                colors: ["#008FFB"],
                title: {
                    text: 'HeatMap Chart (Single color)'
                },
            }
        };
    }

    componentDidMount() {
        const socket = socketIOClient("http://localhost:4002");
        socket.on("FingerProbs", new_data => {
            let int_data = JSON.parse(new_data);
            let series = this.state.series;
            for (let i = 0; i < 10; i++) {
                series[i].data.shift();
                series[i].data.push({ x: "" + this.state.counter, y: (int_data[i] * 100) });
            }
            if (this.state.buffer !== 5)
                this.setState(state => ({
                    buffer: state.buffer + 1,
                    counter: state.counter + 1,
                    series,
                    options: state.options,
                }));
            else {
                this.setState(state => ({
                    buffer: 0,
                    counter: state.counter + 1,
                    series,
                    options: state.options,
                }));
                ApexCharts.exec('heatmap', 'updateSeries', series);
            }
        });
    }
    render() {
        return (
            <div className="app">
                <div className="row">
                    <div className="mixed-chart">
                        <Chart
                            options={this.state.options}
                            series={this.state.series}
                            type="heatmap"
                            width="1000"
                            height="300"
                        />
                    </div>
                </div>
            </div>
        );
    }
}

export default Heatmap;


