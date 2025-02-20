let sessionSocket = null;

function getUserId() {
  return document.getElementById("user_id").textContent;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Check if the cookie starts with the name
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function fetchCookie() {
  const csrftoken = getCookie("csrftoken");
  try {
    const response = await fetch("/browse/getcookkie/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({
        cookie: document.cookie,
      }),
    });
    console.log(response.status);
    const result = await response.json();
    console.log(result);
    if (result.status === "OK") {
      console.log("Cookie saved successfully.");
    } else {
      console.error("Failed to save the cookie."), result.status.e;
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

let isHovering = false;
let lastSentX = null;
let lastSentY = null;

function getCursor(event) {
  let bounds = img.getBoundingClientRect();
  let x = event.clientX - bounds.left;
  let y = event.clientY - bounds.top;
  return { x, y };
}

function sendHoverData(x, y) {
  const message = {
    user_id: getUserId(),
    special: "hover",
    message: { x, y },
  };
  sessionSocket.send(JSON.stringify(message));
}

// Function to track mouse movement
function trackMouse(event) {
  isHovering = true;
  let { x, y } = getCursor(event);
  moveLens({ x, y });

  // Update last cursor position
  lastSentX = x;
  lastSentY = y;
}

// Check and send hover data every second
setInterval(() => {
  if (isHovering && lastSentX !== null && lastSentY !== null) {
    sendHoverData(lastSentX, lastSentY);
  }
}, 1000);

function repeatAndSendHover() {
  const imgContainer = document.querySelector(".img-container");
  imgContainer.addEventListener("mousemove", trackMouse);
  imgContainer.addEventListener("mouseenter", () => {
    isHovering = true;
  });
  imgContainer.addEventListener("mouseleave", () => {
    isHovering = false;
    lens.style.display = "none";
  });
}

repeatAndSendHover();

function displayimage(imagestr) {
  const imageContainer = document.querySelector("#browser_screenshot");
  imageContainer.src = `data:image/png;base64, ${imagestr}`;
}

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playFrequencies(frequencies, duration = 0.5) {
  let startTime = audioCtx.currentTime;
 console.log("playing batch")
  function playNext(index) {
    if (index >= frequencies.length) return; // Stop if all frequencies are played

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = "sine"; // You can change this to 'square', 'sawtooth', or 'triangle'
    oscillator.frequency.setValueAtTime(
      frequencies[index],
      audioCtx.currentTime
    );

    // Connect the nodes
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    // console.log(`Playing frequency: ${frequencies[index]} Hz`);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + duration);

    // Schedule next frequency after `duration` seconds
    setTimeout(() => playNext(index + 1), duration * 1000);
  }

  playNext(0); // Start playing the first frequency
}


function getScreen() {
  let imageContainer = document.getElementById("imagecon");
  let computedStyle = window.getComputedStyle(imageContainer);
  return `${computedStyle.width}X${computedStyle.height}`
}

function estabilish_socket(user_id) {
  button.textContent = "connecting socket .";
  sessionSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/" + "browse/" + user_id + "/"
  );
  sessionSocket.binaryType = "blob";
  sessionSocket.onopen = () => {
    console.log("WebSocket connection successfully established!");
    setTimeout(() => {
      sessionSocket.send(
        JSON.stringify({
          user_id: user_id,
          message: "Hello from client!",
          special: "hello",
        })
      );
    }, 1000);
    setTimeout(() => {
      sessionSocket.send(
        JSON.stringify({
          special: "start_stream",
          user_id: user_id,
        })
      );
    }, 1000);
    button.textContent = "connected socket .";
  };
sessionSocket.onmessage = async (event) => {
  try {
    if (typeof event.data === "string") {
      let trimmedData = event.data.trim();

      // Check if it starts and ends correctly
      if (!(trimmedData.startsWith("{") && trimmedData.endsWith("}"))) {
        console.error("Invalid JSON format:", trimmedData);
        return;
      }

      // Attempt to parse
      const data = JSON.parse(trimmedData);

      if (data.type === "i" && data.screen || data.audio) {
        displayimage(data.screen);

        if (typeof data.audio === "string") {
          try {
            let audioArray = data.audio.split(",").map(Number);
            if (Array.isArray(audioArray)) {
              playFrequencies(audioArray);
            } else {
              console.error("Audio data is not an array:", audioArray);
            }
          } catch (error) {
            console.error("Failed to parse audio JSON:", error);
          }
        }
      } else {
        console.warn("Unknown message type or missing data:", data);
      }
    } else {
      console.warn("Unknown WebSocket message type:", typeof event.data);
    }
  } catch (err) {
    console.error("Failed to handle WebSocket message:", err);
  }
};


  sessionSocket.onerror = (error) => {
    console.error("WebSocket encountered an error:", error);
  };

  sessionSocket.onclose = (event) => {
    console.log("WebSocket connection closed:", event);
  };

  return sessionSocket;
}

function startAsession(userid) {
  console.log("Starting the session for user:", userid);
  let screendex = getScreen()
  const url = `${window.location.origin}/browse/start_session/${userid}/${screendex}/`;
  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `Failed to start session: ${response.status} ${response.statusText}`
        );
      }
      return response.json();
    })
    .then((data) => {
      if (data.status === "OK") {
        console.log("Session started successfully:", data);
        button.textContent =
          "session started successfully . loading screens ...";
        sessionSocket = estabilish_socket(userid);
      } else {
        console.error(
          "Session failed to start:",
          data.message || "Unknown error"
        );
      }
    })
    .catch((error) => {
      console.error("An error occurred:", error.message);
    });
}

function send_chat_to_llm() {
  // first tell to source page 
  // let message = document.getElementById("chat").value;
  sessionSocket.send(
    JSON.stringify({
      "user_id": getUserId(),
      "special": "page_source",
      "message": "chat"
    })
  )
  console.log("sending chat to llm")
}

document.getElementById("browser_screenshot").addEventListener("click", function (event) {
  const rect = this.getBoundingClientRect(); // Get image position
  const mouseX = event.clientX - rect.left; // Mouse X relative to the image
  const mouseY = event.clientY - rect.top; // Mouse Y relative to the image
  console.log("Clicked at relative coordinates (X, Y):", mouseX, mouseY);
  console.log("calling click event")
  const message = {
    user_id: getUserId(),
    special: "click_on_driver",
    message: {
      x: mouseX,
      y: mouseY,
    },
  };
  sessionSocket.send(JSON.stringify(message));
});

function detect_pressed_key() {
  document.addEventListener("keypress", () => {
    const key = event.key;
    console.log("Key pressed:", key);
    const message = {
      user_id: getUserId(),
      special: "keypress",
      message: {
        key: key
      },
    };
    sessionSocket.send(JSON.stringify(message));
  })
}

// Attach event listener
const search_button = document.querySelector("#search_btn");
search_button.addEventListener("click", function () {
  let querry = document.getElementById("search").value
  sessionSocket.send(
    JSON.stringify({
      "user_id": getUserId(),
      "querry": querry,
      "special":"search"
    })
  )
});

const chat_button = document.querySelector("#ai-chat");
chat_button.addEventListener("click", function () {
  send_chat_to_llm();
});

// Attach event listener
const button = document.querySelector("#startSessionButton");
button.addEventListener("click", function () {
  const userid = getUserId();
  startAsession(userid);
});

detect_pressed_key();
fetchCookie();
