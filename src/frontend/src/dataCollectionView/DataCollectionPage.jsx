import React, { useState } from "react";

import { Container } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import EventList from "./EventList";
import GuidedRecorder from "./GuidedRecorder";
import SessionInfoForm from "./SessionInfoForm";
import { newSession } from "./Bridge";
import { format, getDateTime } from "./Utilities";
import SelfDirectedRecorder from "./SelfDirectedRecorder";
import InTheAirRecorder from "./InTheAirRecorder";
import TouchTypeRecorder from "./TouchTypeRecorder";
import GuidedInTheAirRecorder from "./GuidedInTheAirRecorder";
import { EnterIdSnackbar, EnterPromptSnackbar, RecordingStoppedSnackbar } from "./snackbars";

const useStyles = makeStyles(theme => ({
  root: {
    margin: theme.spacing() * 4
  }
}));

function DataCollection() {
  const [recording, setRecording] = useState(false);
  const [id, setId] = useState("");
  const [customPrompts, setCustomPrompts] = useState("");
  const [notes, setNotes] = useState("");
  const [mode, setMode] = useState(1);
  const [snackbarIdOpen, setSnackbarIdOpen] = useState(false);
  const [snackbarPromptsOpen, setSnackbarPromptsOpen] = useState(false);
  const [snackbarRecordingStoppedOpen, setSnackbarRecordingStoppedOpen] = useState(false);
  const [events, setEvents] = useState([]);
  const [hand, setHand] = useState("both");
  const [trial, setTrial] = useState(0);

  const classes = useStyles();

  const closeSnackbars = () => {
    setSnackbarIdOpen(false);
    setSnackbarPromptsOpen(false);
    setSnackbarRecordingStoppedOpen(false);
  };

  const stopRecording = () => {
    setRecording(false);
    setTrial(trial => parseFloat(trial) + 1);
    setSnackbarRecordingStoppedOpen(true);
  };

  const click = () => {
    if (!recording) {
      if (id === "") setSnackbarIdOpen(true);
      else if ([2, 3].includes(mode) && customPrompts === "") setSnackbarPromptsOpen(true);
      else {
        closeSnackbars();
        setEvents([]);
        let prompts = mode === 1 ? [
          "left pinkie a",
          "left ring finger s",
          "left middle finger d",
          "left index finger f",
          "right index finger j",
          "right middle finger k",
          "right ring finger l",
          "right pinkie semicolon",
        ].join(" , ")
          : customPrompts;
        newSession({ time: getDateTime(), id, notes, prompts, mode, hand, trial }, () => setRecording(true));
      }
    } else stopRecording();
  };

  const addEvent = event => setEvents(events => [event, ...events]);

  const onPrompt = ({ newPrompt, datetime, timestamp }) => addEvent([
    format(
      'Prompted "{0}" key with {1} {2}',
      newPrompt.key,
      newPrompt.hand,
      newPrompt.finger
    ),
    datetime + format(" ({0})", timestamp)
  ]);

  const onCustomPrompt = ({ newCustomPrompt, datetime, timestamp }) => addEvent([
    format('Prompted "{0}"', newCustomPrompt),
    datetime + format(" ({0})", timestamp),
  ]);

  const onKey = ({ key, datetime, timestamp }) => addEvent([
    format('"{0}" key pressed', key),
    datetime + format(" ({0})", timestamp),
  ]);

  return (
    <div className={classes.root}>
      <EnterIdSnackbar
        open={snackbarIdOpen}
        setOpen={setSnackbarIdOpen}
      />

      <EnterPromptSnackbar
        mode={mode}
        open={snackbarPromptsOpen}
        setOpen={setSnackbarPromptsOpen}
      />

      <RecordingStoppedSnackbar
        open={snackbarRecordingStoppedOpen}
        setOpen={setSnackbarRecordingStoppedOpen}
      />

      <Container maxWidth="xl">
        <SessionInfoForm
          {...{
            click,
            closeSnackbars,
            customPrompts,
            hand,
            id,
            mode,
            notes,
            recording,
            setCustomPrompts,
            setHand,
            setId,
            setNotes,
            setMode,
            setTrial,
            trial,
          }}
        />
        <br /><br />
        {React.createElement(
          [SelfDirectedRecorder, GuidedRecorder, InTheAirRecorder, TouchTypeRecorder, GuidedInTheAirRecorder][mode],
          { customPrompts, onCustomPrompt, onKey, onPrompt, recording, stopRecording, },
          null,
        )}
        <br /> <br />
        <EventList events={events} />
      </Container>
    </div>
  );
}

export default DataCollection;
