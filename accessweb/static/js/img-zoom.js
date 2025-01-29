// Get elements
const imgContainer = document.querySelector(".img-container");
const img = document.querySelector(".img-container img");
const lens = document.querySelector(".lens");

// Controls
const checkVisuals = document.getElementById("checkvisuals");
const zoomRange = document.getElementById("zoom-range");
const widthRange = document.getElementById("width-range");
const fontRange = document.getElementById("font_range");

// Default zoom level
let zoom = parseFloat(zoomRange.value);
let lastCursorPos = { x: img.width / 2, y: img.height / 2 };

// Create a canvas element to copy the image
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");

// Function to draw image onto the canvas
function updateCanvas() {
  const imgWidth = img.width;
  const imgHeight = img.height;

  // Resize canvas to match the image size
  canvas.width = imgWidth;
  canvas.height = imgHeight;

  // Draw the image onto the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, imgWidth, imgHeight);
}

// Get cursor position relative to image
function getCursor(event) {
  let bounds = img.getBoundingClientRect();
  let x = event.clientX - bounds.left;
  let y = event.clientY - bounds.top;
  return { x, y };
}

// Update lens properties and ensure correct zoom effect
function updateLens() {
  if (!checkVisuals.checked) {
    lens.style.display = "none";
    return;
  }

  lens.style.width = `${widthRange.value}px`;
  lens.style.height = `${widthRange.value}px`;
  lens.style.display = "block";

  // Update lens background using the canvas image
  lens.style.backgroundImage = `url(${canvas.toDataURL()})`; // Use canvas image as background

  // Apply zoom level to background size
  lens.style.backgroundSize = `${img.width * zoom}px ${img.height * zoom}px`;

  // Update lens position immediately after zoom
  moveLens(lastCursorPos); // Ensure lens updates correctly
}

// Function to move the lens based on cursor position
function moveLens(pos) {
  if (!checkVisuals.checked) return;

  let cursorX = pos.x;
  let cursorY = pos.y;
  lastCursorPos = { x: cursorX, y: cursorY }; // Store last position

  const halfLensWidth = lens.offsetWidth / 2;
  const halfLensHeight = lens.offsetHeight / 2;

  let lensLeft = cursorX - halfLensWidth;
  let lensTop = cursorY - halfLensHeight;

  // Ensure lens stays within image bounds
  if (lensLeft < 0) lensLeft = 0;
  if (lensTop < 0) lensTop = 0;
  if (lensLeft + lens.offsetWidth > img.width)
    lensLeft = img.width - lens.offsetWidth;
  if (lensTop + lens.offsetHeight > img.height)
    lensTop = img.height - lens.offsetHeight;

  lens.style.left = `${lensLeft}px`;
  lens.style.top = `${lensTop}px`;

  // Adjust zoomed background position based on cursor position
  let bgX = -(cursorX * zoom - halfLensWidth);
  let bgY = -(cursorY * zoom - halfLensHeight);

  lens.style.backgroundPosition = `${bgX}px ${bgY}px`;
}

// Enable zoom effect when mouse moves over the image
function enableZoom() {
  imgContainer.addEventListener("mousemove", (event) => {
    lens.style.display = "block";
    moveLens(getCursor(event));
  });

  imgContainer.addEventListener("mouseleave", () => {
    lens.style.display = "none";
  });

  // Update the canvas and lens background on image load and src change
  const observer = new MutationObserver(() => {
    img.onload = () => {
      updateCanvas();
      updateLens();
    };
    updateCanvas(); // Ensure the canvas is updated when image changes
    updateLens(); // Ensure lens updates immediately
  });

  observer.observe(img, { attributes: true, attributeFilter: ["src"] });
}

// Event Listeners for UI Controls
zoomRange.addEventListener("input", () => {
  zoom = parseFloat(zoomRange.value);
  updateLens();
});

widthRange.addEventListener("input", updateLens);
checkVisuals.addEventListener("change", updateLens);

fontRange.addEventListener("input", () => {
  document.body.style.fontSize = `${fontRange.value}px`;
});

// Initialize zoom functionality
enableZoom();
updateLens();
