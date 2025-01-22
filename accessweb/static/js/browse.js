const button = document.getElementById("start_session");

function getUserId() {
  return document.getElementById("user_id").textContent;
}

function startAsession(userid) {
  console.log("starting the session for user:", userid);
}

// Attach event listener
button.addEventListener("click", function () {
  const userid = getUserId(); // Fetch the user ID when the button is clicked
  startAsession(userid);
});
