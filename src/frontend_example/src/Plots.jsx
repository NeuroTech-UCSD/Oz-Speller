import React, { Component } from "react";
// import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend} from 'recharts';
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
    // plugins: {
    //   streaming: {
    //     frameRate: 15
    //   }
    // },
    // animation: {
    //   duration: 0
    // },
    // hover: {
    //   animationDuration: 0
    // },
    // responsiveAnimationDuration: 0
    animation: false,
    tooltips: {
      enabled: false,
    },
    events: []
  };

const options2 = {
  title: {
    display: true,
    text: 'psd'
  },
  responsive: false,
  scales: {
    xAxes: [
      {
        // id: 'time-axis',
        type: 'linear',
        ticks: {
          max: 10,
          min: 0,
          stepSize: 1
        },
        scaleLabel: {
          display: true,
          labelString: 'Time'
        }
      },
    ],
    yAxes: [{
      scaleLabel: {
        display: true,
        labelString: 'value'
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
        refresh: 250,
      },
      ticks: {
        display: false,
        // autoSkip: false,
        // maxTicksLimit: 10
      }
    },
  ]},
  // plugins: {
  //   streaming: {
  //     frameRate: 15
  //   }
  // },
  // animation: {
  //   duration: 0
  // },
  // hover: {
  //   animationDuration: 0
  // },
  // responsiveAnimationDuration: 0
  // animation: false,
  // animations: {
  //   enabled: true,
  //   easing: 'linear',
  //   dynamicAnimation: {
  //     speed: 1000
  //   }
  // },
  stroke: {
    curve: 'smooth'
  },
  tooltips: {
    enabled: false,
  },
  events: []
};

class Plots extends Component {
    constructor() {
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
      const datasets2 = [];
      for (let i = 1; i < 9; i++) {
        datasets2.push({
          label: "Channel " + i,
          // yAxisID: 'live-axis',
          borderColor: colors[i - 1],
          backgroundColor: colors[i - 1],
          // lineTension: 0.3,
          pointRadius: 0,
          // borderDash: [8, 4],
          data: [{
            x: 1,
            y: Math.random()
          },
          {
            x: 2,
            y: Math.random()
          },
          {
            x: 3,
            y: Math.random()
          },
          {
            x: 4,
            y: Math.random()
          },
          {
            x: 5,
            y: Math.random()
          }],
          hidden: false,
          fill: false,
        });
      };
      this.data = {datasets};
      this.data2 = {datasets:datasets2};
      this.options = options;
      this.options2 = options2;
      console.log(this.data)
      console.log(this.data2)
    }

    componentDidMount() {
      const socket = socketIOClient("http://localhost:4002");
      socket.on("my response", (data) => {
          console.log(data)
      });
      socket.on("background", (new_data) => {
          // console.log(data['data']);
          // this.data = data['data'];
          // console.log(this.data);
          for (let i = 0; i < this.data.datasets.length; i++) {
            this.data.datasets[i].data.push({
              // x: new_data["timestamp"],
              x: Date.now(),
              y: new_data["value"][i]
              // x: Date.now(),
              // y: Math.random()
            });
          }
      });

      socket.on("background2", (new_data) => {
        // console.log(data['data']);
        // this.data = data['data'];
        // console.log(this.data);
        for (let i = 0; i < this.data2.datasets.length; i++) {
          this.data2.datasets[i].data = [{
            x: 1,
            y: Math.random()
          },
          {
            x: 2,
            y: Math.random()
          },
          {
            x: 3,
            y: Math.random()
          },
          {
            x: 4,
            y: Math.random()
          },
          {
            x: 5,
            y: Math.random()
          }];
        }
      });
    }

    render() {
        return (<div>
            <Line data={this.data} options={this.options} height={300} width={1000} />
            {/* // <Line data={this.data} height={300} width={1000} /> */}
            <Line data={this.data2} options={this.options2} height={300} width={1000} />
            </div>
        );
    }
}

export default Plots;