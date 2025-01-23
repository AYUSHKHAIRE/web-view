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
    console.log(response.status)
    const result = await response.json();
    console.log(result)
    if (result.status === "OK") {
      console.log("Cookie saved successfully.");
    } else {
      console.error("Failed to save the cookie."), result.status.e;
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

function estabilish_socket(user_id) {
  button.textContent = "connecting socket .";
  const sessionSocket = new WebSocket(
    "ws://" +
    window.location.host +
    "/ws/" +
    "browse/" +
    user_id +
    "/"
  );
  setTimeout(() => {
    sessionSocket.send(`connected to session ${user_id}`);
  }, 1000);
  button.textContent = "connected socket ."
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
    return response.json(); // Parse the response as JSON
  })
    .then((data) => {
      if (data.status == 'OK') {
        console.log("Session started successfully:", data);
        button.textContent = "session started successfully . loading screens ..."
        estabilish_socket(userid);
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
    const userid = getUserId(); // Fetch the user ID when the button is clicked
  startAsession(userid);
});

fetchCookie();