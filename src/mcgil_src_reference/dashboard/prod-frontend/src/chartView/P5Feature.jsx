import React, { Component } from "react";
import Sketch from "react-p5";
import socketIOClient from "socket.io-client";

export default class App extends Component {
  setup = (p5, canvasParentRef) => {
    const feature = this.props.feature || "var";
    const sketchHeight = this.props.height;
    const sketchWidth = this.props.width;
    const numSamples = Math.round(this.props.numSeconds / 0.1) || 50;
    const xAxisHeight = 40;
    const yAxisWidth = 100;
    const numRows = 8;
    const w = (sketchWidth - yAxisWidth) / numSamples;
    const h = (sketchHeight - xAxisHeight) / numRows;
    const leftMargin = 10;

    const BUFFER_DIST_SECONDS = this.props.distSeconds || 0.1;
    const socket = socketIOClient("http://localhost:4002");

    // @todo make sure finger labels are aligned with predictions
    let rowLabels = [
      "Channel 1",
      "Channel 2",
      "Channel 3",
      "Channel 4",
      "Channel 5",
      "Channel 6",
      "Channel 7",
      "Channel 8",
    ];

    let probsData = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]];

    function updateChart(newData) {
      // probs array with shape 10

      // console.log(newData["var"]);
      probsData.push(newData[feature].reverse());
      if (probsData.length > numSamples) {
        probsData.splice(0, 1);
      }

      for (let i = 0; i < probsData.length; i++) {
        for (let j = 0; j < numRows; j++) {
          // values range from 0 to 1. Multiply value by colors length and floor it
          let maxRow = probsData.map(function (row) {
            return Math.max.apply(Math, row);
          });
          let max = Math.max.apply(null, maxRow);
          p5.fill(calculateColor(probsData[i][j] / max));
          p5.rect(i * w + yAxisWidth, (numRows - j - 1) * h, w, h);
        }
      }
      displayAxis();
    }

    function displayLabels() {
      // y-labels
      p5.fill("black");
      p5.strokeWeight(0);
      for (let i = 0; i < rowLabels.length; i++) {
        p5.text(rowLabels[i], 0 + leftMargin, i * h + h * 0.65);
      }

      // x-labels
      for (let i = Math.round(numSamples * BUFFER_DIST_SECONDS); i >= 0; i--) {
        p5.text(
          i,
          sketchWidth -
            (i * (sketchWidth - yAxisWidth)) /
            (numSamples * BUFFER_DIST_SECONDS) -
            8,
          sketchHeight - xAxisHeight / 3
        );
      }
    }

    function displayAxis() {
      // y-axis
      p5.strokeWeight(1);
      p5.stroke(0);
      for (let i = 0; i < numRows + 1; i++) {
        p5.line(0 + yAxisWidth, h * i, sketchWidth, h * i);
      }
      p5.strokeWeight(0);
    }

    const calculateColor = (ratio) => {
      let color1 = "0000FF";
      let color2 = "FFFFFF";
      let hex = function (x) {
        x = x.toString(16);
        return x.length === 1 ? "0" + x : x;
      };

      let r = Math.ceil(
        parseInt(color1.substring(0, 2), 16) * ratio +
          parseInt(color2.substring(0, 2), 16) * (1 - ratio)
      );
      let g = Math.ceil(
        parseInt(color1.substring(2, 4), 16) * ratio +
          parseInt(color2.substring(2, 4), 16) * (1 - ratio)
      );
      let b = Math.ceil(
        parseInt(color1.substring(4, 6), 16) * ratio +
          parseInt(color2.substring(4, 6), 16) * (1 - ratio)
      );

      return "#" + (hex(r) + hex(g) + hex(b));
    };
    // use parent to render canvas in this ref (without that p5 render this canvas outside your component)
    p5.createCanvas(sketchWidth, sketchHeight).parent(canvasParentRef);
    p5.strokeWeight(0);
    p5.stroke(0);
    p5.background(240);
    p5.fill("white");
    p5.rect(yAxisWidth, 0, sketchWidth - yAxisWidth, sketchHeight);
    displayAxis();
    displayLabels();

    socket.on("Feature_Data", function (data) {
      updateChart(data["Feature_Data"]);
    });
  };

  render() {
    return (
      <>
        <h1>{this.props.feature || "var"} Values</h1>
        <Sketch setup={this.setup} draw={this.draw} />
      </>
    );
  }
}
