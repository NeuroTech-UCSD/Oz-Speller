import React, { useEffect, useState } from "react";

import { Typography } from "@material-ui/core";

import { sendCustomPrompt } from "./Bridge";
import ProgressBar from "./ProgressBar";

import Hands from "./hand.png";
import Green from "./green.png";
import "./dataCollection.css";
import { getDateTime } from "./Utilities";

const TTlookup = JSON.parse(
  '{"space":"right thumb","q":"left pinkie","a":"left pinkie","z":"left pinkie","w":"left ring finger","s":"left ring finger","x":"left ring finger","e":"left middle finger","d":"left middle finger","c":"left middle finger","r":"left index finger","t":"left index finger","f":"left index finger","g":"left index finger","v":"left index finger","b":"left index finger","y":"right index finger","u":"right index finger","h":"right index finger","j":"right index finger","n":"right index finger","m":"right index finger","i":"right middle finger","k":"right middle finger","o":"right ring finger","l":"right ring finger","p":"right pinkie"}'
);
const handGraphicLookup = {
  "left pinkie": "a",
  "left ring finger": "s",
  "left middle finger": "d",
  "left index finger": "f",
  "right index finger": "j",
  "right middle finger": "k",
  "right ring finger": "l",
  "right pinkie": "semicolon",
  "right thumb": "space"
};

function TouchTypeRecorder({
  recording,
  onCustomPrompt,
  customPrompts,
  stopRecording
}) {
  const text = customPrompts
    .toLowerCase()
    .replace(/[^a-z ]/gi, "") // Restrict to letters & space
    .replace(/\r?\n|\r/g, " ") // Replace newline chars with spaces
    .trim();
  const prompts = [
    { character: "", finger: "" },
    ...text
      .split("")
      .map(character => (character === " " ? "space" : character))
      .map(character => ({ character, finger: TTlookup[character] }))
  ];

  const [promptIndex, setPromptIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const updateInterval = 30; // in ms

    let interval = setInterval(() => {
      if (recording) {
        if (progress === 0) {
          if (promptIndex < prompts.length - 1) setPromptIndex(i => i + 1);
          else stopRecording();
        }

        setProgress(progress => progress + (updateInterval / 2000) * 100);
        if (progress === 80 || progress === 81) {
          let parts = prompts[promptIndex].finger.split(' ');
          sendCustomPrompt(
            {
              newCustomPrompt: prompts[promptIndex].finger + ' - ' + prompts[promptIndex].character,
              finger: parts.slice(1).join(' '),
              hand: parts[0],
              key: prompts[promptIndex].character,
              time: getDateTime(),
            },
            onCustomPrompt
          );
        }

        if (progress >= 100) setProgress(0);
      } else {
        setProgress(0);
        setPromptIndex(0);
      }
    }, updateInterval);
    return () => clearInterval(interval);
  }, [
    onCustomPrompt,
    progress,
    promptIndex,
    prompts,
    recording,
    stopRecording
  ]);

  return (
    <div>
      <div className="notGrey">
        <ProgressBar percent={progress} />
        <div className="line">
          <img width="25px" align="center" src={Green} alt="" />
        </div>
      </div>
      <Typography variant="h4">
        {recording ? (
          <>
            Press the "{prompts[promptIndex].character}" key with your{" "}
            {prompts[promptIndex].finger} when the bar reaches the green dot
          </>
        ) : (
            <>Waiting...</>
          )}
      </Typography>

      <div style={{ overflow: "auto", whiteSpace: "nowrap", marginBottom: 14 }}>
        <Typography display="inline" variant="h5">
          {prompts
            .slice(Math.max(0, promptIndex - 25), promptIndex)
            .map(prompt => prompt.character)
            .map(char => (char === "space" ? '\u00A0' : char))
            .join("")}
        </Typography>
        <Typography display="inline" variant="h4" color="secondary">
          <u>
            {prompts[promptIndex].character === "space"
              ? '\u00A0'
              : prompts[promptIndex].character}
          </u>
        </Typography>
        <Typography display="inline" variant="h5">
          {prompts
            .slice(promptIndex + 1)
            .map(prompt => prompt.character)
            .map(char => (char === "space" ? '\u00A0' : char))
            .join("")}
        </Typography>
      </div>

      {recording &&
        (progress > 80 ? (
          <div className="notGrey">
            <div className="image1">
              <img width="40%" src={Hands} alt="" />
            </div>
            <div className={handGraphicLookup[prompts[promptIndex].finger]}>
              <img width="3%" src={Green} alt="" />
            </div>
          </div>
        ) : (
            <div className="parent">
              <div className="image1">
                <img width="40%" src={Hands} alt="" />
              </div>
              <div className={handGraphicLookup[prompts[promptIndex].finger]}>
                <img width="3%" src={Green} alt="" />
              </div>
            </div>
          ))}
    </div>
  );
}

export default TouchTypeRecorder;
