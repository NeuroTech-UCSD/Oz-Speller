export async function newSession({ time, id, notes, prompts, mode, hand, trial }, callback) {
  let [timestamp, datetime] = time;

  fetch(
    "http://localhost:5000/new-session?datetime=" +
    datetime +
    "&timestamp=" +
    timestamp +
    "&id=" +
    encodeURIComponent(id) +
    "&notes=" +
    encodeURIComponent(notes.replace(/(?:\r\n|\r|\n)/g, "\\n")) +
    "&mode=" +
    ["Self-directed", "Guided", "In-the-air", "Guided-in-the-air", "Guided-in-the-air"][mode] +
    "&prompts=" +
    encodeURIComponent(prompts.replace(/(?:\r\n|\r|\n)/g, "\\n").replace(/"/g, '\\"')) +
    "&hand=" +
    hand +
    "&trial=" +
    trial
  )
    .then(res => callback({ res, datetime, timestamp }))
    .catch(console.log);
}

export async function sendData({ key, time }, callback) {
  if (key === " ")
    key = "space";

  let [timestamp, datetime] = time;
  fetch(
    "http://localhost:5000/data-collection?datetime=" +
    datetime +
    "&timestamp=" +
    timestamp +
    "&key=" +
    key
  )
    .then(res => callback({ res, datetime, timestamp, key }))
    .catch(console.log);
}

export async function sendPrompt({ newPrompt, time }, callback) {
  let [timestamp, datetime] = time;

  fetch(
    "http://localhost:5000/prompt?datetime=" +
    datetime +
    "&timestamp=" +
    timestamp +
    "&hand=" +
    newPrompt.hand +
    "&finger=" +
    newPrompt.finger
  )
    .then(res => callback({ res, datetime, timestamp, newPrompt }))
    .catch(console.log);
}

export async function sendCustomPrompt({ time, newCustomPrompt, hand, finger, key }, callback) {
  let [timestamp, datetime] = time;
  fetch(
    "http://localhost:5000/custom-prompt?datetime=" +
    datetime +
    "&timestamp=" +
    timestamp +
    (!!newCustomPrompt ? "&prompt=" + newCustomPrompt : "") +
    (!!hand ? "&hand=" + hand : "") +
    (!!finger ? "&finger=" + finger : "") +
    (!!key ? "&key=" + key : "")
  )
    .then(res => callback({ res, datetime, timestamp, newCustomPrompt }))
    .catch(console.log);
}