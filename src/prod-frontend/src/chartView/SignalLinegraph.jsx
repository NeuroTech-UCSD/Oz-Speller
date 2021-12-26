import React, { Component } from "react";
import "moment";

import { Line } from "react-chartjs-2";
import "chartjs-plugin-streaming";
import socketIOClient from "socket.io-client";



const options = {
  backgroundColor:'rgb(0,0,0)',
  title: {
    display: true,
    text: 'Push data feed sample'
  },
  height: 500,
  width: 500,
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
        id: 'live-axis',
        type: 'realtime',
        realtime: {
          duration: 10000,
          delay: 0,
          refresh: 2500,
          // onRefresh: function () {
          //   if (Math.random() < .01) {
          //   data.datasets[0].data.push({
          //     x: Date.now(),
          //     y: Math.random() 
          //   });
          // }
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
        labelString: 'uVrms'
      }
    }]
  },
  tooltips: {
    enabled: false,
  },
  plugins: {
    // streaming: false
    streaming: {
      frameRate: 10
    }
  },
  animation: false
};

class ChartJsComponent extends Component {
  constructor() {
    super();
    const data = {
      datasets: []
    };

    const colors = ["#808081", "#7B4A8C", "#36569C", "#317058", "#DBB10E", "#FA5D34", "#DE382D", "#A05131"];

    for (let i = 0; i < 8; i++) {
      data.datasets.push(
        {
          label: "Channel " + (i + 1) + " Filtered",
          xAxisID: 'live-axis',
          borderColor: colors[i],
          backgroundColor: colors[i],
          lineTension: 0,
          borderDash: [8, 4],
          data: [{
            x: Date.now(),
            y: Math.random()
          }],
          fill: false,
        },
        {
          label: "Channel " + (i + 1) + " Unfiltered",
          xAxisID: 'live-axis',
          borderColor: colors[i],
          backgroundColor: colors[i],
          lineTension: 0,
          borderDash: [8, 4],
          data: [{
            x: Date.now(),
            y: Math.random()
          }],
          fill: false,
          hidden: true,
        }
      );
    }

    this.state = {
      response: [0, 0, 0, 0, 0, 0, 0, 0],
      endpoint: "http://localhost:4002",
      data: data,
      options: options
    };

  }

  componentDidMount() {
    console.log("Chart Mounted");
    const { endpoint } = this.state;
    const socket = socketIOClient(endpoint);
    socket.on("Signal_Data", new_data => {
      // console.log("Signal data: " + new_data);
      const int_data = JSON.parse(new_data["data"])
      // let int_data = JSON.parse(new_data);
      // barData.datasets[0].data = int_data;
      // console.log(int_data);
      for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 2; j++) {
          this.state.data.datasets[i * 2 + j].data.push({
            x: new_data["timestamp"],
            y: int_data[j][i]
          });
        }
      }
    })
  }

  render() {
    return (
      <Line data={this.state.data} options={options} height={400} width={1200} />
      // <Line
      //   data={barData}
      //   width={100}
      //   height={50}
      //   options={{ maintainAspectRatio: true }}
      // />
    )

  }
}

export default ChartJsComponent;

// For Reference
// function shuffle(array) {
//   let counter = array.length;
// 
//   // While there are elements in the array
//   while (counter > 0) {
//     // Pick a random index
//     let index = Math.floor(Math.random() * counter);
// 
//     // Decrease counter by 1
//     counter--;
// 
//     // And swap the last element with it
//     let temp = array[counter];
//     array[counter] = array[index];
//     array[index] = temp;
//   }
// 
//   return array;
// }
// 
// 
// 
// 

// 
