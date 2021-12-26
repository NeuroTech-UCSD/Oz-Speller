import React from "react";

import {
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  FormControlLabel,
  RadioGroup,
  Radio,
  FormLabel
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  fullWidth: {
    width: "100%"
  },
  selectFormControl: {
    minWidth: 120
  }
});

function SessionInfoForm({
  click,
  recording,
  id,
  setId,
  notes,
  setNotes,
  customPrompts,
  setCustomPrompts,
  mode,
  setMode,
  trial,
  setTrial,
  setHand,
  closeSnackbars
}) {
  const classes = useStyles();

  let radioButtonExtraProps = {};
  if (recording) radioButtonExtraProps = { disabled: true };

  return (
    <Grid container spacing={4} alignItems="flex-start">
      <Grid item xs={4}>
        <TextField
          className={classes.fullWidth}
          InputProps={{
            readOnly: recording
          }}
          label="Subject ID"
          margin="dense"
          onChange={event => setId(event.target.value)}
          variant={recording ? "filled" : "outlined"}
          width={1}
          value={id}
        />
        <br />
        <br />
        <FormControl className={classes.selectFormControl}>
          <InputLabel>Recording mode</InputLabel>
          <Select
            inputProps={{ readOnly: recording }}
            onChange={event => {
              closeSnackbars();
              setMode(event.target.value);
            }}
            value={mode}
            variant={recording ? "filled" : "standard"}
          >
            <MenuItem value={0}>
              <b>Self-directed:</b>&nbsp;type at your own pace; no prompt
            </MenuItem>
            <MenuItem value={1}>
              <b>Guided:</b>&nbsp;receive set prompts to type keys
            </MenuItem>
            <MenuItem value={2}>
              <b>In the air:</b>&nbsp;respond to timed custom commands
            </MenuItem>
            <MenuItem value={3}>
              <b>Touch-Type:</b>&nbsp;touch-type a text prompt ITA
            </MenuItem>
            <MenuItem value={4}>
              <b>Guided in the air:</b>&nbsp;set key prompts without registering presses
            </MenuItem>
          </Select>
        </FormControl>
        <br />
        <br />
        <Button
          className={classes.fullWidth}
          color="primary"
          onClick={click}
          size="medium"
          variant="contained"
          width={1}
        >
          {recording ? "Stop" : "Start"} recording
        </Button>
      </Grid>
      {(mode === 2 || mode === 3) && (
        <Grid item xs>
          <TextField
            className={classes.fullWidth}
            InputProps={{
              readOnly: recording
            }}
            label={mode === 2 ? "Custom prompts (separate by commas)" : "Text to type"}
            margin="dense"
            multiline
            onChange={event => setCustomPrompts(event.target.value)}
            variant={recording ? "filled" : "outlined"}
            width={1}
            rows={7}
            value={customPrompts}
          />
        </Grid>
      )}
      <Grid item xs>
        <TextField
          className={classes.fullWidth}
          InputProps={{
            readOnly: recording
          }}
          label="Extra notes"
          margin="dense"
          multiline
          onChange={event => setNotes(event.target.value)}
          rows={7}
          value={notes}
          variant={recording ? "filled" : "outlined"}
        />
      </Grid>

      <Grid item xs={4}>
        <TextField
          id="standard-helperText"
          label="Trial Number"
          margin="dense"
          defaultValue={trial}
          onChange={event => setTrial(event.target.value)}
          variant={recording ? "filled" : "outlined"}
        />
        <br />
        <br />
        <FormControl component="fieldset">
          <FormLabel component="legend">Hand Recorded</FormLabel>
          <RadioGroup
            aria-label="position"
            name="position"
            defaultValue="both"
            onChange={event => setHand(event.target.value)}
            row
          >
            <FormControlLabel
              value="right"
              control={<Radio color="primary" />}
              label="Right"
              {...radioButtonExtraProps}
            />
            <FormControlLabel
              value="left"
              control={<Radio color="primary" />}
              label="Left"
              {...radioButtonExtraProps}
            />
            <FormControlLabel
              value="both"
              control={<Radio color="primary" />}
              label="Both"
              {...radioButtonExtraProps}
            />
          </RadioGroup>
        </FormControl>
      </Grid>
    </Grid>
  );
}

export default SessionInfoForm;
