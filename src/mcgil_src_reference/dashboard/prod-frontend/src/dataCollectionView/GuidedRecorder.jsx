import React, { useCallback, useEffect, useState } from "react";

import { Typography } from "@material-ui/core";

import { sendData, sendPrompt } from "./Bridge";
import ProgressBar from "./ProgressBar";
import { choice, getDateTime } from "./Utilities";

import Hands from "./hand.png";
import Green from "./green.png";
import "./dataCollection.css";

function GuidedRecorder({ recording, onKey, onPrompt }) {
  const fingers = [
    { hand: "left", finger: "pinkie", key: "a" },
    { hand: "left", finger: "ring finger", key: "s" },
    { hand: "left", finger: "middle finger", key: "d" },
    { hand: "left", finger: "index finger", key: "f" },
    { hand: "right", finger: "index finger", key: "j" },
    { hand: "right", finger: "middle finger", key: "k" },
    { hand: "right", finger: "ring finger", key: "l" },
    { hand: "right", finger: "pinkie", key: "semicolon" }
  ];

  const [progress, setProgress] = useState(0);
  const [prompt, setPrompt] = useState(choice(fingers));
  const [keyQueue, setKeyQueue] = useState([]);

  useEffect(() => {
    const updateInterval = 30;

    let interval = setInterval(() => {
      if (recording) {
        setProgress(progress => progress + (updateInterval / 3000) * 100);

        if (progress === 80) {
          let newPrompt = prompt;
          sendPrompt({ newPrompt, time: getDateTime(), }, onPrompt);
        }

        if (progress >= 100) {
          setProgress(0);

          let newPrompt = choice(fingers);
          setPrompt(newPrompt);
        }
      } else setProgress(0);
    }, updateInterval);

    return () => clearInterval(interval);
  }, [fingers, onPrompt, progress, prompt, recording]);

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
      <div className="notGrey">
        <ProgressBar percent={progress} />
        <div className="line">
          <img width="25px" align="center" src={Green} alt="" />
        </div>
      </div>

      <Typography variant="h4">
        {recording
          ? `Press the ${prompt.key} key when the bar reaches the green dot`
          : "Waiting..."}
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

      {recording &&
        (progress > 80 ? (
          <div className="notGrey">
            <div className="image1">
              <img width="40%" src={Hands} alt="" />
            </div>
            <div className={prompt.key}>
              <img width="3%" src={Green} alt="" />
            </div>
          </div>
        ) : (
            <div className="parent">
              <div className="image1">
                <img width="40%" src={Hands} alt="" />
              </div>
              <div className={prompt.key}>
                <img width="3%" src={Green} alt="" />
              </div>
            </div>
          ))}
    </div>
  );
}

export default GuidedRecorder;
