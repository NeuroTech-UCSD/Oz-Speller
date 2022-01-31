import React, { useState } from "react";

import { Divider, Paper, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import "./predictionWidget.css";
import { choice } from "../Utilities";

import handBlank from "./hands/blank.png";
import handA from "./hands/a.png";
import handS from "./hands/s.png";
import handD from "./hands/d.png";
import handF from "./hands/f.png";
import handJ from "./hands/j.png";
import handK from "./hands/k.png";
import handL from "./hands/l.png";
import handSemicolon from "./hands/semicolon.png";

const handImages = { blank: handBlank, a: handA, s: handS, d: handD, f: handF, j: handJ, k: handK, l: handL, semicolon: handSemicolon };

console.log(handImages);

const useStyles = makeStyles(theme => ({
  divider: {
    marginBottom: theme.spacing() * 2,
    marginTop: theme.spacing() * 2
  }
}));

function PredictionWidget({ paperCN }) {
  const classes = useStyles();

  const [prediction, setPrediction] = useState(choice(Object.keys(handImages)));

  return (
    <Paper className={paperCN} elevation={3}>
      <Typography variant="h4">Predictions</Typography>
      <Divider className={classes.divider} />
      <div className="image1">
        <img width="100%" src={handImages[prediction]} alt="" />
      </div>
    </Paper>
  );
}

export default PredictionWidget;
