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

function displayimage(imagestr) {
  imagecotainer = document.querySelector("#browser_screenshot");
  imagecotainer.src = `data:image/png;base64, ${imagestr}`;
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
        // Handle JSON messages
        const data = JSON.parse(event.data); // Parse the JSON string into an object
        console.log("Received JSON message:", data);

        if (data.type === "i" && data.message) {
          displayimage(data.message); // Call your displayimage function with the Base64 image data
        } else {
          console.warn("Unknown message type or missing data:", data);
        }
      } else if (event.data instanceof Blob) {
        // Handle binary messages (Blob)
        console.log("Received binary message (Blob).");

        const arrayBuffer = await event.data.arrayBuffer(); // Convert Blob to ArrayBuffer
        const binaryData = new Uint8Array(arrayBuffer); // Convert ArrayBuffer to Uint8Array
        const base64String = btoa(
          binaryData.reduce(
            (data, byte) => data + String.fromCharCode(byte),
            ""
          )
        );
        displayimage(base64String); // Display the image
        console.log("displayed", base64String);
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
  const url = `${window.location.origin}/browse/start_session/${userid}`;
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

// Attach event listener
const button = document.querySelector("#startSessionButton");
button.addEventListener("click", function () {
  const userid = getUserId();
  startAsession(userid);
});

fetchCookie();
