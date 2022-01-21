import React, { Component } from "react";
import Sketch from "react-p5";
import socketIOClient from "socket.io-client";
 
export default class App extends Component {


  // file:///home/gautierk/Projects/Dashboard-NeuroTech/p5/index.html

    // updateChart(probsData[0]);

  setup = (p5, canvasParentRef) => {

  let sketchHeight = 400;
  let sketchWidth = 800;
  let numSamples = 100;
  let numFingers = 10;
  let w = sketchWidth / numSamples;
  let h = sketchHeight / numFingers;
  const socket = socketIOClient('http://localhost:4002');
  let fingerLabels = ['Nothing', 'Right Thumb', 'Right Index', 'Right Middle', 'Right Ring', 'Right Pinky', 'Left Index', 'Left Middle', 'Left Ring', 'Left Pinky'];

  let colors = ["#f7fbff", "#e1edf8", "#cbdff1", "#abd0e6", "#82badb", "#59a2cf", "#3787c0", "#1b6aaf", "#084d97", "#08306b"];

  let probsData = [[0, 0.2, 0.8, 0, 0, 0, 0, 0, 0, 0]];
  let color_id = 0;

    function updateChart(newData) { // probs array with shape 10

      newData = JSON.parse(newData);
      newData = newData.map(val => Number(val));
      console.log(newData);
      probsData.push(newData);
      if (probsData.length > numSamples) {
        probsData.splice(0, 1);
      }

      for (let i = 0; i < probsData.length; i++) { //x
        for (let j = 0; j < numFingers; j++) { // y
          // values range from 0 to 1. Multiply value by colors length and floor it
          color_id = Math.floor(probsData[i][j] * (colors.length - 1));
          // probsData[i][j] 
          // console.log(color_id);
          // console.log(colors[color_id]);
          p5.fill(colors[color_id]);
          // x, y, w, h
          p5.rect(i * w, (numFingers - j - 1) * h, w, h);
        }
      }
      p5.fill(0, 0, 0, 0);
      p5.strokeWeight(2);
      p5.stroke(51);
      p5.rect(0, 0, sketchWidth, sketchHeight);
      p5.strokeWeight(0);

  };

    p5.createCanvas(sketchWidth, sketchHeight).parent(canvasParentRef); // use parent to render canvas in this ref (without that p5 render this canvas outside your component)
    p5.strokeWeight(0);
    p5.stroke(0);
    p5.background(220);


    socket.on("FingerProbs", function (data) {
      updateChart(data);
    });
  }


  //draw = p5 => {
  //  p5.background(0);
  //  p5.ellipse(this.x, this.y, 70, 70);
  //  // NOTE: Do not use setState in draw function or in functions that is executed in draw function... pls use normal variables or class properties for this purposes
  //  this.x++;
  //};
 
  render() {
    return <Sketch setup={this.setup} draw={this.draw} />;
  }
}
