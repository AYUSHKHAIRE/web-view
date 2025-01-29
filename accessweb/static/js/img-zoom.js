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
let lastCursorPos = { x: img.width / 2, y: img.height / 2 }; // Store last cursor position

// Get cursor position relative to image
function getCursor(event) {
  let bounds = img.getBoundingClientRect();
  let x = event.clientX - bounds.left;
  let y = event.clientY - bounds.top;
  return { x, y };
}

// Update lens properties
function updateLens() {
  if (!checkVisuals.checked) {
    lens.style.display = "none";
    return;
  }

  lens.style.width = `${widthRange.value}px`;
  lens.style.height = `${widthRange.value}px`;
  lens.style.display = "block";

  // 🔥 Explicitly update the background image and force a repaint
  lens.style.backgroundImage = `url(${img.src})`;
  lens.style.backgroundSize = `${img.width * zoom}px ${img.height * zoom}px`;
  lens.style.backgroundPosition = "0px 0px"; // Reset background position

  moveLens({ x: lastCursorPos.x, y: lastCursorPos.y }); // Ensure zoom effect updates
}

// Move lens based on cursor
function moveLens(pos) {
  if (!checkVisuals.checked) return;

  let cursorX = pos.x;
  let cursorY = pos.y;

  lastCursorPos = { x: cursorX, y: cursorY }; // Store last position

  const halfLensWidth = lens.offsetWidth / 2;
  const halfLensHeight = lens.offsetHeight / 2;

  let lensLeft = cursorX - halfLensWidth;
  let lensTop = cursorY - halfLensHeight;

  // Ensure lens stays within bounds
  if (lensLeft < 0) lensLeft = 0;
  if (lensTop < 0) lensTop = 0;
  if (lensLeft + lens.offsetWidth > img.width)
    lensLeft = img.width - lens.offsetWidth;
  if (lensTop + lens.offsetHeight > img.height)
    lensTop = img.height - lens.offsetHeight;

  lens.style.left = `${lensLeft}px`;
  lens.style.top = `${lensTop}px`;

  let bgX = -(cursorX * zoom - halfLensWidth);
  let bgY = -(cursorY * zoom - halfLensHeight);

  lens.style.backgroundSize = `${img.width * zoom}px ${img.height * zoom}px`;
  lens.style.backgroundPosition = `${bgX}px ${bgY}px`;
}

// Enable zoom functionality
function enableZoom() {
  imgContainer.addEventListener("mousemove", (event) => {
    moveLens(getCursor(event));
  });

  imgContainer.addEventListener("mouseleave", () => {
    lens.style.display = "none";
  });

  // Observe changes in image src and update lens background
  const observer = new MutationObserver(() => {
    img.onload = () => {
      updateLens();
    };
    updateLens(); // Immediately update in case image is already loaded
  });

  observer.observe(img, { attributes: true, attributeFilter: ["src"] });
}

// Event Listeners for Controls
zoomRange.addEventListener("input", () => {
  zoom = parseFloat(zoomRange.value);
  updateLens();
});

widthRange.addEventListener("input", () => {
  updateLens();
});

checkVisuals.addEventListener("change", () => {
  updateLens();
});

fontRange.addEventListener("input", () => {
  document.body.style.fontSize = `${fontRange.value}px`;
});

// Initialize
enableZoom();
updateLens();
