/*

define this somewhere in your HTML or component

<div id="braildiv" class="braildiv">
  <div class="mainbrailstrip" id="mainbrailstrip">
    <div class="brailcol" id="brailcol1">
      <div id="braildot1" class="dot braildot"></div>
      <div id="braildot2" class="dot braildot"></div>
      <div id="braildot3" class="dot braildot"></div>
    </div>
    <div class="brailcol" id="brailcol2">
      <div id="braildot4" class="dot braildot"></div>
      <div id="braildot5" class="dot braildot"></div>
      <div id="brailcol6" class="dot braildot"></div>
    </div>
  </div>
</div>;

add these styles 

.brail-reader .mainbrailcolordiv{
  width: 80vw;
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000000;
  position: fixed;
}

.braildiv .mainbrailstrip{
  display: flex;
  align-items: center;
  text-align: center;
  justify-content: center;
  flex-direction: row;
}

.brailcol{
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  flex-direction: column;
}

.brailcol .dot{
  display: flex;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #ffffff;
  margin: 30px;
  border: 2px double white;
}
  
*/


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
        decodedString += " "; // Ensure spaces are decoded properly
      } else {
        decodedString += this.utf8Dict[key] || "?"; // '?' for unknown sequences
      }
    }
    return decodedString.trim();
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
        encodedString += letter + " "; // Preserve spaces & unknown characters
      }
    }
    return encodedString.trim();
  }
}

const braille = new BrailBelt();
let track = new Array(9).fill(" "); // Fixed 9 spaces
let text_being_carried = "try to click here";

function prepare_track(full_text) {
  track.fill(" "); // Reset track

  let middleIndex = Math.floor(track.length / 2);
  let startIndex = Math.max(middleIndex - Math.floor(full_text.length / 2), 0);
  let endIndex = Math.min(startIndex + full_text.length, track.length);

  for (let i = startIndex, j = 0; i < endIndex; i++, j++) {
    track[i] = full_text[j];
  }

  updateDisplay();
}

function updateDisplay() {
  let middleIndex = Math.floor(track.length / 2);

  for (let i = 0; i < track.length; i++) {
    let button_target = document.getElementById("brail-english-letter-" + i);
    if (button_target) {
      button_target.textContent = track[i];
    }
  }

  let currentMiddleLetter = track[middleIndex].trim() || " ";
  let brailleCode = braille.encodeString(currentMiddleLetter);
  display_a_letter_in_brail(brailleCode);
}
function display_a_letter_in_brail(numbers) {
  let all_dots = document.getElementsByClassName("braildot");
  for (let dot of all_dots) {
    dot.style.backgroundColor = "black"; // Reset
  }

  if (numbers === "") return; // If it's a space, don't activate any dots

  for (let num of numbers) {
    let target_dot = document.getElementById("braildot" + num);
    if (target_dot) {
      target_dot.style.backgroundColor = "white"; // Activate Braille dots
    }
  }
}

function updateTrack(clickedIndex) {
  let middleIndex = Math.floor(track.length / 2);
  let clickedLetter = track[clickedIndex];

  if (clickedLetter.trim() === "") return; // Ignore empty clicks

  // Find the relative occurrence of the clicked letter inside track
  let relativeCount = 0;
  for (let i = 0; i < clickedIndex; i++) {
    if (track[i] === clickedLetter) {
      relativeCount++;
    }
  }

  // Find the corresponding occurrence in text_being_carried
  let letterIndex = -1;
  let count = 0;
  for (let i = 0; i < text_being_carried.length; i++) {
    if (text_being_carried[i] === clickedLetter) {
      if (count === relativeCount) {
        letterIndex = i;
        break;
      }
      count++;
    }
  }

  if (letterIndex === -1) return; // If the letter isn't found, do nothing

  // Adjust to prevent cutting off the last letters
  let newStart = Math.max(letterIndex - middleIndex, 0);
  let newEnd = Math.min(newStart + track.length, text_being_carried.length);

  let trimmedText = text_being_carried.slice(newStart, newEnd);

  track.fill(" "); // Reset track
  let insertIndex = Math.max(middleIndex - (letterIndex - newStart), 0);

  for (
    let i = 0, j = insertIndex;
    i < trimmedText.length && j < track.length;
    i++, j++
  ) {
    track[j] = trimmedText[i];
  }

  updateDisplay();
}

// Attach event listeners after DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  prepare_track(text_being_carried);

  for (let index = 0; index < track.length; index++) {
    let element = document.getElementById("brail-english-letter-" + index);
    if (element) {
      element.addEventListener("click", function () {
        updateTrack(index);
      });
    }
  }
});
