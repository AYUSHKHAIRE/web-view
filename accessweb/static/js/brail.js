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
        // Number indicator detected
        numDetectedFlag = true;
        continue;
      }

      let key = numDetectedFlag ? `3456 ${seq}` : seq;
      numDetectedFlag = false; // Reset flag

      let utf8Seq = this.utf8Dict[key] || "?"; // '?' for unknown sequences
      decodedString += utf8Seq;
    }
    return decodedString.trim();
  }
}

// Example usage:
const braille = new BrailBelt();
let encoded = braille.encodeString("hello123");
console.log(`Encoded: ${encoded}`);
let decoded = braille.decodeString(encoded);
console.log(`Decoded: ${decoded}`);

function display_a_letter_in_brail(numbers) {
  all_dots = document.getElementsByClassName("braildot");
  for (i = 0; i < all_dots.length; i++) {
    all_dots[i].style.backgroundColor = "black";
  }
  for (i = 0; i < numbers.length; i++) {
    target_dot = document.getElementById("braildot" + numbers[i]);
    target_dot.style.backgroundColor = "white";
  }
}

let a = braille.encodeString("a");
display_a_letter_in_brail(a);
