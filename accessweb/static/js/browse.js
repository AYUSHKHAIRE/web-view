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
  let image = document.querySelector("#browser_screenshot");
  let bounds = image.getBoundingClientRect();
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
  if (imagestr.length > 100) {
    imageContainer.src = `data:image/png;base64, ${imagestr}`;
  } else {
    imageContainer.src = `https://cdn.dribbble.com/userupload/19849667/file/original-95fabf09850cd28e919f3e156fca3cea.gif`;
  }
}

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playFrequencies(frequencies, duration = 0.5) {
  let startTime = audioCtx.currentTime;
  console.log("playing batch");
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
  return `${computedStyle.width}X${computedStyle.height}`;
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
    button.textContent = "Session started .";
    let stop_button = document.querySelector("#stopSessionButton");
    stop_button.style.display = "block";
    let start_button = document.querySelector("#startSessionButton");
    start_button.style.display = "none";
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

        if ((data.type === "i" && data.screen) || data.audio) {
          displayimage(data.screen);

          if (typeof data.audio === "string") {
            try {
              let audioArray = data.audio.split(",").map(Number);
              if (Array.isArray(audioArray)) {
                // playFrequencies(audioArray);
              } else {
                console.error("Audio data is not an array:", audioArray);
              }
            } catch (error) {
              console.error("Failed to parse audio JSON:", error);
            }
          }
        } else if (data.type === "LLM_response") {
          console.log(data);
          display_LLM_response(data);
        } else if (data.type === "vision_response") {
          console.log(data);
          highlightTextOnImage(
            data.message,
            "browser_screenshot",
            "imagehighlightoverlay"
          );
        } else if (data.type === "text_response") {
          console.log(data);
        } else if (data.type === "stream_stopped") {
          console.log("stream stopped");
          const stop_url = `${window.location.origin}/browse/stop_session/${user_id}/`;
          fetch(stop_url, {
            method: "GET",
          })
            .then((response) => response.json()) // Parse JSON response
            .then((data) => {
              if (data.status === "OK") {
                // Check JSON field correctly
                console.log("Session stopped successfully");
                let stop_button = document.querySelector("#stopSessionButton");
                button.textContent = "Session stopped .";
                stop_button.style.display = "none";
                let start_button = document.querySelector(
                  "#startSessionButton"
                );
                start_button.style.display = "block";
                start_button.textContent = "start session";
                let screen = document.getElementById("browser_screenshot");
                screen.src = `https://cdn.dribbble.com/userupload/19849667/file/original-95fabf09850cd28e919f3e156fca3cea.gif`;
              } else {
                console.error("Failed to stop session:", data);
              }
            })
            .catch((error) => console.error("Fetch error:", error));
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
  let screendex = getScreen();
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

function send_chat_source_to_llm(actual_input) {
  // first tell to source page
  // let message = document.getElementById("chat").value;
  sessionSocket.send(
    JSON.stringify({
      user_id: getUserId(),
      special: "page_source",
      message: "chat",
    })
  );
  sessionSocket.send(
    JSON.stringify({
      user_id: getUserId(),
      special: "LLM_ask_a_text",
      message: actual_input,
    })
  );
  let cb = document.querySelector("#ai-chat");
  cb.textContent = "send";
  cb.disabled = false;
  let new_div = document.createElement("div");
  new_div.classList.add("chat-outgoing", "chat");
  new_div.innerHTML = actual_input;
  let llmcon = document.getElementById("LLM-conversation");
  llmcon.appendChild(new_div);
  llmcon.scrollTop = llmcon.scrollHeight;
  console.log("sending chat source to llm");
}

document
  .getElementById("browser_screenshot")
  .addEventListener("click", function (event) {
    const rect = this.getBoundingClientRect(); // Get image position
    const mouseX = event.clientX - rect.left; // Mouse X relative to the image
    const mouseY = event.clientY - rect.top; // Mouse Y relative to the image
    console.log("Clicked at relative coordinates (X, Y):", mouseX, mouseY);
    console.log("calling click event");
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
  document.addEventListener("keydown", (event) => {
    const key = event.key;
    console.log("Key pressed:", key);

    let is_allow = document.getElementById("type_kb").checked; // Ensure the checkbox is checked
    if (is_allow) {
      console.log("Sending keypress to server, allowed");
      const message = {
        user_id: getUserId(),
        special: "keypress",
        message: {
          key: key,
        },
      };
      sessionSocket.send(JSON.stringify(message));
    }
  });
}

function speakText(text) {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  synth.speak(utterance);
  console.log("Speaking:", text);
}

function display_LLM_response(data) {
  let llmcon = document.getElementById("LLM-conversation");
  let newmessage;
  try {
    // First, parse `data.message`, since it's a stringified JSON
    let parsedMessage = JSON.parse(data.message);
    // Extract the actual response text
    newmessage = parsedMessage.response;
  } catch (error) {
    console.error("Failed to parse message:", error, "Original:", data.message);
    return;
  }

  // Create a reply container
  let reply_container = document.createElement("div");
  reply_container.classList.add("incoming-chat", "chat");

  // Convert Markdown to HTML (assuming `marked` is available)
  let rawHTML = marked.parse(newmessage);
  reply_container.innerHTML = rawHTML + "<br>";

  // Create a speaker icon button
  let speakerButton = document.createElement("button");
  speakerButton.classList.add("speaker-button");
  speakerButton.innerHTML = "📢";

  // Use "click" event to trigger speech
  speakerButton.addEventListener("click", () => {
    speakText(newmessage);
  });

  // Append elements to chat UI
  reply_container.appendChild(speakerButton);
  llmcon.appendChild(reply_container);
  llmcon.scrollTop = llmcon.scrollHeight;

  console.log("All LLM responses displayed with Markdown.");
}


function highlightTextOnImage(textData, imageid, overlayimagehighlightid) {
  console.log("Received textData (raw):", textData);
  const imageElement = document.getElementById(imageid);
  const overlayElement = document.getElementById(overlayimagehighlightid);

  try {
    if (typeof textData === "string") {
      textData = JSON.parse(textData);
      console.log("Parsed textData:", textData);
    }
  } catch (error) {
    console.error("Error parsing JSON:", error);
    return;
  }

  if (!textData || typeof textData !== "object" || !textData.text) {
    console.error("Error: textData is invalid.", textData);
    return;
  }

  const textEntries = Object.entries(textData.text).map(([text, bbox]) => ({
    text: text,
    bounding_box: bbox,
  }));

  const imgWidth = imageElement.naturalWidth;
  const imgHeight = imageElement.naturalHeight;
  const displayWidth = imageElement.clientWidth;
  const displayHeight = imageElement.clientHeight;

  console.log("Image dimensions:", imgWidth, imgHeight);
  console.log("Displayed size:", displayWidth, displayHeight);

  const scaleX = displayWidth / imgWidth;
  const scaleY = displayHeight / imgHeight;

  console.log("Scale factors:", scaleX, scaleY);

  overlayElement.innerHTML = "";

  textEntries.forEach((item) => {
    const bbox = item.bounding_box;
    if (!Array.isArray(bbox) || bbox.length !== 4) return;

    // Get bounding box coordinates
    const x1 = bbox[0].x * scaleX;
    const y1 = bbox[0].y * scaleY;
    const x2 = bbox[2].x * scaleX;
    const y2 = bbox[2].y * scaleY;

    const width = x2 - x1;
    const height = y2 - y1;

    console.log(
      `Highlighting "${item.text}" at (${x1}, ${y1}, ${width}, ${height})`
    );

    const highlightBox = document.createElement("div");
    highlightBox.style.position = "absolute";
    highlightBox.style.left = `${x1}px`;
    highlightBox.style.top = `${y1}px`;
    highlightBox.style.width = `${width}px`;
    highlightBox.style.height = `${height}px`;
    highlightBox.style.border = "2px solid red";
    highlightBox.style.backgroundColor = "rgba(219, 216, 44, 0.34)";
    highlightBox.style.pointerEvents = "none";
    overlayElement.appendChild(highlightBox);
  });
}

let max_highlight = 5;
function send_request_for_highlight() {
  console.log("sending request for highlight");
  const highlight_con = document.getElementById("imagehighlightoverlay");
  const highlight_button = document.getElementById("highlight-chat-button");
  if (highlight_con.style.display === "none") {
    if (max_highlight > 0) {
      max_highlight -= 1;
      highlight_con.style.display = "block";
      sessionSocket.send(
        JSON.stringify({
          user_id: getUserId(),
          special: "vision_ask_a_vision",
          message: "Hello ! have you read the message ?",
        })
      );
      highlight_button.textContent = "remove highlight";
    } else {
      highlight_con.style.display = "block";
      highlight_button.textContent = "limit over . cannot highlight more .";
    }
  } else {
    highlight_con.style.display = "None";
    highlight_button.textContent = "show highlight";
  }
}

function stop_stream() {
  sessionSocket.send(
    JSON.stringify({
      user_id: getUserId(),
      special: "stop_stream",
    })
  );
  console.log("stopped stream , consulting threads");
  let screen = document.getElementById("browser_screenshot");
  screen.src = `https://cdn.dribbble.com/userupload/19849667/file/original-95fabf09850cd28e919f3e156fca3cea.gif`;
}

// stop button
const stop_button = document.querySelector("#stopSessionButton");
stop_button.addEventListener("click", function () {
  stop_stream();
  button.textContent = "Session stopped .";
  setTimeout(() => {
    sessionSocket.close();
    console.log("Session stopped.");
  }, 3000);
});

// Attach event listener
const search_button = document.querySelector("#search_btn");
search_button.addEventListener("click", function () {
  let querry = document.getElementById("search").value;
  sessionSocket.send(
    JSON.stringify({
      user_id: getUserId(),
      querry: querry,
      special: "search",
    })
  );
});

const chat_button = document.querySelector("#ai-chat");
chat_button.addEventListener("click", function () {
  any_input = document.querySelector("#ai-chat-input");
  if (any_input.value.length > 0) {
    ai_input = any_input.value;
    send_chat_source_to_llm(ai_input);
    any_input.value = "";
  }
});

const hi_button = document.querySelector("#highlight-chat-button");
hi_button.addEventListener("click", function () {
  send_request_for_highlight();
});

// Attach event listener
const button = document.querySelector("#startSessionButton");
button.addEventListener("click", function () {
  const userid = getUserId();
  startAsession(userid);
});

const camera_on_button = document.getElementById("turn-on-camera");
const sign_video = document.getElementById("sign-video");
const canvas = document.createElement("canvas");
let camera_stream = null;
let captureInterval = null;

async function requestCameraPermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    stream.getTracks().forEach((track) => track.stop()); // Immediately stop to just check permission
    return true; // Permission granted
  } catch (error) {
    console.error("Camera access denied or blocked: ", error);
    alert("Please allow camera access in your browser settings.");
    return false; // Permission denied
  }
}

camera_on_button.addEventListener("click", async function () {
  if (!camera_stream) {
    // Check for permission first
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) return;

    // Turn ON camera
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((videoStream) => {
        camera_stream = videoStream;
        sign_video.srcObject = camera_stream;
        sign_video.play(); // Ensure the video starts playing
        camera_on_button.textContent = "Stop Camera";
      })
      .catch((error) => {
        console.error("Error accessing the camera: ", error);
      });
  } else {
    // Turn OFF camera
    camera_stream.getTracks().forEach((track) => track.stop()); // Stop all tracks
    sign_video.srcObject = null; // Remove video feed
    camera_stream = null; // Reset stream variable
    camera_on_button.textContent = "Start Camera";
  }
});

function captureFrame() {
  if (
    !camera_stream ||
    sign_video.videoWidth === 0 ||
    sign_video.videoHeight === 0
  )
    return;

  const ctx = canvas.getContext("2d");
  canvas.width = sign_video.videoWidth;
  canvas.height = sign_video.videoHeight;
  ctx.drawImage(sign_video, 0, 0, canvas.width, canvas.height);

  const base64Data = canvas.toDataURL("image/png");
  console.log("Captured Base64:", base64Data); // Log Base64 output
  sessionSocket.send(
    JSON.stringify({
      user_id: getUserId(),
      special: "recognize_sign",
      message: "Hello ! have you read the sign ?",
      base64_cam: base64Data,
    })
  );
}

sign_video.addEventListener("mouseenter", function () {
  if (!captureInterval) {
    captureInterval = setInterval(captureFrame, 3000); // Capture every 3 seconds
  }
});

sign_video.addEventListener("mouseleave", function () {
  clearInterval(captureInterval);
  captureInterval = null;
});

detect_pressed_key();
fetchCookie();
