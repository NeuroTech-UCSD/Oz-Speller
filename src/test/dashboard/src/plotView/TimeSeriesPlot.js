import React, { Component } from "react";
import { Line } from "react-chartjs-2";
import "chartjs-plugin-streaming";
import socketIOClient from "socket.io-client";

const options = {
    title: {
        display: true,
        text: 'timeseries'
    },
    responsive: false,
    scales: {
        xAxes: [
            {
                id: 'time-axis',
                type: 'linear',
                ticks: {
                    max: 0,
                    min: -10,
                    stepSize: 1
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            },
            {
                gridLines: {
                    display: false
                },
                id: 'live-axis',
                type: 'realtime',
                realtime: {
                    duration: 10000,
                    delay: 0,
                    refresh: 100,
                },
                ticks: {
                    display: false,
                    // autoSkip: false,
                    // maxTicksLimit: 10
                }
            },
        ],
        yAxes: [{
            scaleLabel: {
            display: true,
            labelString: 'value'
            }
        }]
    },
    animation: false,
    tooltips: {
        enabled: false,
    },
    events: []
};

class TimeSeriesPlot extends Component {
    constructor () {
        super()
        const colors = ["#808081", "#7B4A8C", "#36569C", "#317058", "#DBB10E", "#FA5D34", "#DE382D", "#A05131"];
        const datasets = [];
        for (let i = 1; i < 9; i++) {
            datasets.push({
            label: "Channel " + i,
            xAxisID: 'live-axis',
            borderColor: colors[i - 1],
            backgroundColor: colors[i - 1],
            // lineTension: 0.3,
            pointRadius: 0,
            // borderDash: [8, 4],
            data: [{
                x: Date.now(),
                y: Math.random(),
            }],
            hidden: false,
            fill: false,
            });
        };
        this.data = {datasets};
        this.options = options;
    }
    componentDidMount() {
        const socket = socketIOClient("http://localhost:4002");
        socket.on("background", (new_data) => {
            for (let i = 0; i < this.data.datasets.length; i++) {
              this.data.datasets[i].data.push({
                x: Date.now(),
                y: new_data["value"][i]
              });
            }
        });
    }
    render() {
        return (
            <Line data={this.data} options={this.options} height={300} width={1000} />
        );
    }
}

export default TimeSeriesPlot;