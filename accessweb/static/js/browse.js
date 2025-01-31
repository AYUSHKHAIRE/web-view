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
  const imageContainer = document.querySelector("#browser_screenshot");
  imageContainer.src = `data:image/png;base64, ${imagestr}`;
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
    const startTime = performance.now(); // Start timing

    if (typeof event.data === "string") {
      const data = JSON.parse(event.data); // Parse the JSON string into an object

      const parseEndTime = performance.now(); // Time after parsing JSON
      // console.log(
      //   `[ WEBSOCKET ] Time taken to parse JSON: ${(
      //     parseEndTime - startTime
      //   ).toFixed(4)} ms`
      // );

      if (data.type === "i" && data.screen) {
        const displayStartTime = performance.now(); // Start timing display
        displayimage(data.screen); // Call your displayimage function with the Base64 image data
        const displayEndTime = performance.now(); // End timing display
        // console.log(
        //   `[ DISPLAY IMAGE ] Time taken to display image: ${(
        //     displayEndTime - displayStartTime
        //   ).toFixed(4)} ms`
        // );
      } else {
        console.warn("Unknown message type or missing data:", data);
      }
    } else {
      console.warn("Unknown WebSocket message type:", typeof event.data);
    }

    const endTime = performance.now(); // End timing for the entire onmessage handler
    // console.log(
    //   `[ WEBSOCKET ] Total time to process message: ${(
    //     endTime - startTime
    //   ).toFixed(4)} ms`
    // );
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

document.getElementById("browser_screenshot").addEventListener("click", function (event) {
  const rect = this.getBoundingClientRect(); // Get image position
  const mouseX = event.clientX - rect.left; // Mouse X relative to the image
  const mouseY = event.clientY - rect.top; // Mouse Y relative to the image
  console.log("Clicked at relative coordinates (X, Y):", mouseX, mouseY);
  console.log("calling click event")
  const message = {
    special: "click_on_driver",
    message: {
      x: mouseX,
      y: mouseY,
    },
  };
  sessionSocket.send(JSON.stringify(message));
});


// Attach event listener
const button = document.querySelector("#startSessionButton");
button.addEventListener("click", function () {
  const userid = getUserId();
  startAsession(userid);
});

fetchCookie();

