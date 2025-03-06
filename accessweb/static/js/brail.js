class BrailBelt {
  constructor() {
    this.brailleDict = {
      "#": "3456",
      " ": "",
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
      1: "1",
      2: "12",
      3: "14",
      4: "145",
      5: "15",
      6: "124",
      7: "1245",
      8: "125",
      9: "24",
      0: "245",
    };

    this.utf8Dict = {};
    for (let key in this.brailleDict) {
      this.utf8Dict[this.brailleDict[key]] = key; // Reverse mapping
    }
  }

  decodeString(toDecode) {
    if (typeof toDecode !== "string") {
      throw new Error(`${toDecode} should be in string format`);
    }

    let decodedString = "";
    let numMode = false;
    let words = toDecode.split(" ");

    for (let seq of words) {
      if (seq === "3456") {
        numMode = true; // Enable number mode
        continue;
      }

      if (numMode && Object.values(this.brailleDict).includes(seq)) {
        let number = Object.keys(this.brailleDict).find(
          (key) => this.brailleDict[key] === seq
        );
        decodedString += number;
      } else if (seq === "") {
        decodedString += " ";
      } else {
        decodedString += this.utf8Dict[seq] || "?";
        numMode = false; // Reset number mode after a non-number
      }
    }
    return decodedString;
  }

  encodeString(toEncode) {
    if (typeof toEncode !== "string") {
      throw new Error(`${toEncode} should be in string format`);
    }

    let encodedString = "";
    let numMode = false;

    for (let i = 0; i < toEncode.length; i++) {
      let letter = toEncode[i].toLowerCase();

      if (!isNaN(letter) && letter !== " ") {
        // It's a number
        if (!numMode) {
          encodedString += "3456 "; // Add number indicator
          numMode = true;
        }
        encodedString += this.brailleDict[letter]; // No extra space for numbers
      } else {
        numMode = false; // Reset number mode
        encodedString += this.brailleDict[letter]
          ? this.brailleDict[letter] + " "
          : letter + " ";
      }
    }

    return encodedString.trim();
  }
}

const braille = new BrailBelt();
let text_being_carried = "    try to click here 10";
let currentIndex = 0;
let visibleTrackSize = 9;

function preprocessText(text) {
  return text.replace(/\d/g, (match) => `#${match}`);
}

text_being_carried = preprocessText(text_being_carried);

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
      // console.log(num)
    }
  }
  // console.log("displayed" , numbers)
}

function prepare_track(full_text) {
  let firstLetterIndex = full_text.search(/\S/);
  currentIndex = firstLetterIndex >= 0 ? firstLetterIndex : 0;
  updateDisplay();
}

function updateDisplay() {
  let track = new Array(visibleTrackSize).fill(" ");
  let middleIndex = Math.floor(visibleTrackSize / 2);

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

  for (let i = 0; i < visibleTrackSize; i++) {
    let button_target = document.getElementById("brail-english-letter-" + i);
    if (button_target) {
      button_target.textContent = track[i];
    }
  }

  let currentMiddleLetter = text_being_carried[currentIndex] || " ";
  let brailleCode;

  if (currentMiddleLetter === "#") {
    brailleCode = "3456"; // Ensure each digit is handled correctly
    // console.log("Number sign detected, setting braille code to:", brailleCode);
  } else if (
    !isNaN(currentMiddleLetter) &&
    currentIndex > 0 &&
    text_being_carried[currentIndex - 1] === "#"
  ) {
    brailleCode = braille.brailleDict[currentMiddleLetter]; // Direct lookup
  } else {
    brailleCode = braille.encodeString(currentMiddleLetter);
  }

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
