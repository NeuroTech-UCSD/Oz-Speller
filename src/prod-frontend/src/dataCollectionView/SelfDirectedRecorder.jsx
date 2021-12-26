import React, { useCallback, useEffect, useState } from "react";

import { Typography } from "@material-ui/core";

import { sendData } from "./Bridge";
import { getDateTime } from "./Utilities";

function SelfDirectedRecorder({ recording, onKey }) {
  const [keyQueue, setKeyQueue] = useState([]);

  useEffect(() => {
    let id = setInterval(async () => {
      if (keyQueue.length > 0) {
        sendData({ ...keyQueue[0] }, onKey);
        setKeyQueue(keyQueue => keyQueue.slice(1));
      }
    }, 10);
    return () => clearInterval(id);
  }, [keyQueue, onKey]);

  const keyHandler = useCallback(
    async event =>
      recording &&
      setKeyQueue(keyQueue => [
        ...keyQueue,
        { key: event.key, time: getDateTime() }
      ]),
    [recording]
  );

  useEffect(() => {
    document.addEventListener("keydown", keyHandler, false);
    return () => document.removeEventListener("keydown", keyHandler, false);
  }, [keyHandler]);

  return (
    <div>
      <Typography variant="h4">
        {recording ? "Start typing!" : "Waiting..."}
      </Typography>

      {recording && (
        <Typography variant="body1">
          {keyQueue.length} keystrokes in queue to be sent to backend
          {keyQueue.length > 0 && "..."}
        </Typography>
      )}
      {!recording && keyQueue.length > 0 && (
        <Typography variant="body1">
          {keyQueue.length} keystrokes in queue to be sent to backend. Please
          don't start a new recording until all have been sent.
        </Typography>
      )}
    </div>
  );
}

export default SelfDirectedRecorder;
