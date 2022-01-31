import React, { Component } from "react";
import { Line } from "react-chartjs-2";
import "chartjs-plugin-streaming";
import { Typography } from "@material-ui/core";
import socketIOClient from "socket.io-client";

const options = {
  title: {
    display: true,
    text: 'Push data feed sample'
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
          refresh: 1000,
        },
        ticks: {
          display: false,
          autoSkip: false,
          maxTicksLimit: 10
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
  plugins: {
    streaming: {
      frameRate: 15
    }
  },
  animation: {
    duration: 0
  },
  hover: {
    animationDuration: 0
  },
  responsiveAnimationDuration: 0
};



class ChartJsComponent extends Component {
  constructor(props) {
    super(props);

    const colors = ["#808081", "#7B4A8C", "#36569C", "#317058", "#DBB10E", "#FA5D34", "#DE382D", "#A05131"];

    const datasets = [];
    for (let i = 1; i < 9; i++) {
      datasets.push({
        label: "Channel " + i,
        xAxisID: 'live-axis',
        borderColor: colors[i - 1],
        backgroundColor: colors[i - 1],
        lineTension: 0,
        borderDash: [8, 4],
        data: [{
          x: Date.now(),
          y: Math.random(),
        }],
        hidden: false,
        fill: false,
      });
    }

    this.state = {
      feature: props.feature,
      data: { datasets },
      options: options
    };
  }

  componentDidMount() {
    const socket = socketIOClient("http://localhost:4002");
    socket.on("Feature_Data", new_data => {
      for (let i = 0; i < this.state.data.datasets.length; i++)
        this.state.data.datasets[i].data.push({
          x: new_data["timestamp"],
          y: new_data[this.state.feature][i],
        });
    });
  }

  render() {
    return <>
      <Typography variant="h4">
        {this.props.feature}
      </Typography>
      <Line data={this.state.data} options={this.state.options} height={300} width={1000} />
    </>;
  }
}

export default ChartJsComponent;

