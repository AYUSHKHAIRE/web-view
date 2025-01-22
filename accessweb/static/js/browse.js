function getUserId() {
  return document.getElementById("user_id").textContent;
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
