import React, { Component } from "react";
// import {XYPlot, XAxis, YAxis, HorizontalGridLines, LineSeries} from 'react-vis';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend} from 'recharts';
// import * as d3 from "https://cdn.skypack.dev/d3@7";
// import * as d3 from "d3";
// import {values} from "d3/learn-d3-by-example"
// import {Histogram} from "d3/histogram"
import socketIOClient from "socket.io-client";

class Plots extends Component {
    constructor() {
        super()
        this.data = [{name: 'Page A', uv: 400, pv: 340, amt: 2400}, 
                {name: 'Page A', uv: 500, pv: 240, amt: 2400},
                {name: 'Page A', uv: 200, pv: 440, amt: 2400},
                {name: 'Page A', uv: 700, pv: 740, amt: 2400},
                {name: 'Page A', uv: 800, pv: 540, amt: 2400},
                {name: 'Page A', uv: 100, pv: 640, amt: 2400},
                {name: 'Page A', uv: 600, pv: 340, amt: 2400},
                {name: 'Page A', uv: 200, pv: 840, amt: 2400},
                {name: 'Page A', uv: 300, pv: 740, amt: 2400}];
        // this.socket = socketIOClient("http://localhost:4002");
        // this.socket.on("my response", (data) => {
        //     console.log(data)
        // });
    }
    // const socket = socketIOClient("http://localhost:4002");

    // socket.on("send_test", (data) => {
    //     console.log(data)
    // });

    // console.log('data')

    

    // const renderLineChart1 = (
    //     <LineChart width={400} height={400} data={data}>
    //         <Line type="monotone" isAnimationActive={false} dataKey="uv" stroke="#8884d8" />
    //     </LineChart>
    // );

    // const renderLineChart2 = (
    //     <LineChart width={600} height={300} data={data}>
    //       <Line type="monotone" dataKey="uv" stroke="#8884d8" />
    //       <CartesianGrid stroke="#ccc" />
    //       <XAxis dataKey="name" />
    //       <YAxis />
    //     </LineChart>
    // );

    // renderLineChart3 = (
    //     <LineChart width={730} height={250} data={this.data}
    //         margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
    //         <CartesianGrid strokeDasharray="3 3" />
    //         <XAxis dataKey="name" />
    //         <YAxis />
    //         <Tooltip />
    //         <Legend />
    //         <Line type="monotone" isAnimationActive={false} dot={false} dataKey="pv" stroke="#8884d8" />
    //         <Line type="monotone" isAnimationActive={false} dot={false} dataKey="uv" stroke="#82ca9d" />
    //     </LineChart>
    // );

    componentDidMount() {
        const socket = socketIOClient("http://localhost:4002");
        socket.on("my response", (data) => {
            console.log(data)
        });
        socket.on("background", (data) => {
            // console.log(data['data']);
            this.data = data['data'];
            console.log(this.data);

        });
    }

    render() {
        // console.log(this.data)
        // return this.renderLineChart3;
        return (
            <LineChart width={730} height={250} data={this.data}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" isAnimationActive={false} dot={false} dataKey="pv" stroke="#8884d8" />
                <Line type="monotone" isAnimationActive={false} dot={false} dataKey="uv" stroke="#82ca9d" />
            </LineChart>
        );
    }
}

export default Plots;