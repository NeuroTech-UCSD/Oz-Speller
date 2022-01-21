import React from "react";

// import FeaturesChart from "./FeatureLinegraph.jsx";
// import FingerHeatmap from "./FingerPredictionHeatmap.jsx";
// import SignalsChart from "./SignalLinegraph.jsx";

// idea to have two chartpage settings, one for p5 and one for fancy

import P5FingerPredictionHeatmap from "./P5FingerPredictionHeatmap";
import P5Feature from "./P5Feature";

function ChartPage() {
  return (
    <>
      <P5FingerPredictionHeatmap width={1200} height={400} numSeconds={5} />
      <P5Feature width={1200} height={400} numSeconds={5} feature="var" />
    </>
  );
}

export default ChartPage;
