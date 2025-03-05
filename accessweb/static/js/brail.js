class BrailBelt {
  constructor() {
    this.brailleDict = {
      " ": "", // No dots for space
      a: "1",
      b: "12",
      c: "14",
      d: "145",
      e: "15",
      f: "124",
      g: "1245",
      h: "125",
      i: "24",
      j: "245",
      k: "13",
      l: "123",
      m: "134",
      n: "1345",
      o: "135",
      p: "1234",
      q: "12345",
      r: "1235",
      s: "234",
      t: "2345",
      u: "136",
      v: "1236",
      w: "2456",
      x: "1346",
      y: "13456",
      z: "1356",
      1: "3456 1",
      2: "3456 12",
      3: "3456 14",
      4: "3456 145",
      5: "3456 15",
      6: "3456 124",
      7: "3456 1245",
      8: "3456 125",
      9: "3456 24",
      0: "3456 245",
    };

    this.utf8Dict = {};
    for (let key in this.brailleDict) {
      this.utf8Dict[this.brailleDict[key]] = key; // Reverse mapping
    }
  }

  decodeString(toDecode) {
    if (typeof toDecode !== "string") {
      throw new Error(
        `${toDecode} should be in string format, not ${typeof toDecode}`
      );
    }
    let decodedString = "";
    let numDetectedFlag = false;
    let words = toDecode.split(" ");

    for (let i = 0; i < words.length; i++) {
      let seq = words[i];

      if (seq === "3456") {
        numDetectedFlag = true;
        continue;
      }

      let key = numDetectedFlag ? `3456 ${seq}` : seq;
      numDetectedFlag = false;

      if (seq === "") {
        decodedString += " ";
      } else {
        decodedString += this.utf8Dict[key] || "?";
      }
    }
    return decodedString;
  }

  encodeString(toEncode) {
    if (typeof toEncode !== "string") {
      throw new Error(
        `${toEncode} should be in string format, not ${typeof toEncode}`
      );
    }
    let encodedString = "";
    for (let letter of toEncode.toLowerCase()) {
      if (this.brailleDict.hasOwnProperty(letter)) {
        encodedString += this.brailleDict[letter] + " ";
      } else {
        encodedString += letter + " ";
      }
    }
    return encodedString.trim();
  }
}

const braille = new BrailBelt();
let text_being_carried = "    try to click here";
let currentIndex = 0;
let visibleTrackSize = 9;

function display_a_letter_in_brail(numbers) {
  let all_dots = document.getElementsByClassName("braildot");
  for (let dot of all_dots) {
    dot.style.backgroundColor = "black";
  }

  if (numbers === "") return;

  for (let num of numbers) {
    let target_dot = document.getElementById("braildot" + num);
    if (target_dot) {
      target_dot.style.backgroundColor = "white";
    }
  }
}

function prepare_track(full_text) {
  // Find the first non-space character for initial centering
  let firstLetterIndex = full_text.search(/\S/);
  currentIndex = firstLetterIndex >= 0 ? firstLetterIndex : 0;
  updateDisplay();
}

function updateDisplay() {
  let track = new Array(visibleTrackSize).fill(" ");
  let middleIndex = Math.floor(visibleTrackSize / 2);

  // Adjust startIndex to ensure currentIndex is at the center
  let startIndex = Math.max(0, currentIndex - middleIndex);
  let endIndex = Math.min(
    text_being_carried.length,
    startIndex + visibleTrackSize
  );

  for (let i = 0; i < visibleTrackSize; i++) {
    let textIndex = startIndex + i;
    track[i] =
      textIndex < text_being_carried.length
        ? text_being_carried[textIndex]
        : " ";
  }

  // Update displayed letters
  for (let i = 0; i < visibleTrackSize; i++) {
    let button_target = document.getElementById("brail-english-letter-" + i);
    if (button_target) {
      button_target.textContent = track[i];
    }
  }

  // Update Braille representation
  let currentMiddleLetter = text_being_carried[currentIndex] || " ";
  let brailleCode = braille.encodeString(currentMiddleLetter);
  display_a_letter_in_brail(brailleCode);
}

function shiftTrackLeft() {
  if (currentIndex < text_being_carried.length - 1) {
    currentIndex++;
    updateDisplay();
  }
}

function shiftTrackRight() {
  if (currentIndex > 0) {
    currentIndex--;
    updateDisplay();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  prepare_track(text_being_carried);

  for (let index = 0; index < visibleTrackSize; index++) {
    let element = document.getElementById("brail-english-letter-" + index);
    if (element) {
      element.addEventListener("click", function () {
        let clickedIndex =
          currentIndex - Math.floor(visibleTrackSize / 2) + index;
        currentIndex = Math.max(
          0,
          Math.min(text_being_carried.length - 1, clickedIndex)
        );
        updateDisplay();
      });
    }
  }

  document
    .getElementById("brailleft")
    .addEventListener("click", shiftTrackRight);
  document
    .getElementById("brailright")
    .addEventListener("click", shiftTrackLeft);
});

document.addEventListener("keydown", function (event) {
  if (event.key === "ArrowLeft") {
    shiftTrackRight();
  } else if (event.key === "ArrowRight") {
    shiftTrackLeft();
  }
});