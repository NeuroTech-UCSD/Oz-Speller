export function addZero(x, n) {
  while (x.toString().length < n) x = "0" + x;
  return x;
}

export function choice(array) {
  return array[Math.floor(Math.random() * array.length)];
}

export function format(format) {
  var args = Array.prototype.slice.call(arguments, 1);
  return format.replace(/{(\d+)}/g, (match, number) =>
    typeof args[number] != "undefined" ? args[number] : match
  );
}

export function getDateTime() {
  let timestamp = Date.now();
  let datetime = new Date(timestamp);

  return [
    timestamp,
    datetime.getFullYear() +
      "-" +
      addZero(datetime.getMonth() + 1, 2) +
      "-" +
      addZero(datetime.getDate(), 2) +
      "-" +
      addZero(datetime.getHours(), 2) +
      ":" +
      addZero(datetime.getMinutes(), 2) +
      ":" +
      addZero(datetime.getSeconds(), 2) +
      ":" +
      addZero(datetime.getMilliseconds(), 3)
  ];
}
