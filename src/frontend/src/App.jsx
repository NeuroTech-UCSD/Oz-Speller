import React, { useState } from "react";

import { Container, Tab, Tabs, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

// import PredictionWidget from "./PredictionWidget";

import DataCollectionPage from "./dataCollectionView/DataCollectionPage";
import CalibrationPage from "./calibrationView/CalibrationPage";
import ChartPage from "./chartView/ChartPage";
import Plots from "./Plots";
import OfflineData from "./OfflineDataCollection/OfflineData";

const useStyles = makeStyles(theme => ({
  paper: {
    minHeight: 300,
    padding: theme.spacing() * 2,
  },
  root: {
    margin: theme.spacing() * 4
  },
  title: {
    marginBottom: theme.spacing() * 4,
  },
  navigation: {
    marginBottom: theme.spacing(4),
  },
}));

const a11yProps = index => ({
  id: `full-width-tab-${index}`,
  'aria-controls': `full-width-tabpanel-${index}`,
});

function App() {
  const [tab, setTab] = useState(0);

  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Container maxWidth="xl">
        <Typography className={classes.title} variant="h3">
          TritonNeuroTech - Production Dashboard
        </Typography>
        <Tabs
          className={classes.navigation}
          value={tab}
          onChange={(tab, newValue) => setTab(newValue)}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Chart View" {...a11yProps(0)} />
          <Tab label="Data Collection" {...a11yProps(1)} />
          <Tab label="Calibration" {...a11yProps(2)} />
          <Tab label="Plots" {...a11yProps(2)} />
        </Tabs>
      </Container>
      {[<ChartPage />, <OfflineData />, <CalibrationPage />, <Plots />][tab]}
      {/* <Bar_Chart/> */}
      {/*<Signals_Chart/>*/}
      {/* <Features_Chart feature="rms" /> */}
      {/* {[<ChartPage />][tab]} */}
      {/*, <DataCollectionPage />, <CalibrationPage />*/}
    </div>
  );
}

export default App;
