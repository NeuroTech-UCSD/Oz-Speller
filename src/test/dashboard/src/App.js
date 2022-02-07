import React, { Component } from 'react';
import Navigation from './navigation/Navigation';
import CalibrationPage from './calibrationView/CalibrationPage';
import OnlinePredictionPage from './onlinePredictionView/OnlinePredictionPage';
import PlotPage from './plotView/PlotPage';
import './App.css';

class App extends Component {
  constructor() {
    super();
    this.state = {
      route: 'calibration'
    }
  }

  changeRoute = (route) => {
    this.setState({route : route});
  }

  render() {
    return (
      <div className="App">
        <Navigation changeRoute={this.changeRoute} />
        { this.state.route === 'calibration' ? <CalibrationPage/> : 
          this.state.route === 'onlinePrediction' ? <OnlinePredictionPage/> :
          <PlotPage/> // else display Plot Page
        }
      </div>
    );
  }
}

export default App;
