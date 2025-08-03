# 🚀 The Largest Impact: Changing Accessibility Forever

**[Google - The Gemma 3n Impact Challenge](https://www.kaggle.com/competitions/google-gemma-3n-hackathon)**  
**AI for a Better accessibility**
[Read kaggle writeup here](https://www.kaggle.com/competitions/google-gemma-3n-hackathon/writeups/the-largest-impact-changing-accessibility-forever)
---

> _"Is the web really made for me?"_  
> If you are deaf, low-vision, or hearing impaired — the web often feels like a maze.  
> Now, **it finally feels like home**.

**Accessweb** is a transformative step toward universal digital inclusion. It's an AI-powered platform designed to help individuals with **visual or hearing impairments** navigate and use the web independently, with greater ease, comfort, and intelligence.

This is not just a tool.  
This is a mission to fundamentally **break the barriers** of digital access.

---

## Demo

▶️ [Watch the Full Demo on YouTube](https://www.youtube.com/watch?v=Q8R0quSCDU8)
![](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/pictures/thmb.jpg?raw=true)
---

## Key Features

---

### Real-Time Web View

**Purpose**:  
Accessweb provides users with a live, interactive stream of a browser session hosted on the backend. Unlike static page renderers or simplified screen readers, this allows users to interact with real websites in real time — including scrolling, clicking, hovering, and typing — while the system remains aware of accessibility needs.

**How it helps**:  
This bridges the gap between traditional browser interfaces and users who need assistive support. It gives full control over web exploration without requiring the user to handle a complicated browser UI themselves.

**Demo**:  
![session](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/live-session.gif?raw=true)

---

### Zoom Lens

**Purpose**:  
The Zoom Lens is a dynamic magnification tool that overlays a zoomed-in view of any portion of the web page without modifying the underlying DOM or layout. Unlike browser zoom functions that can distort layouts and affect responsiveness, this tool preserves the visual integrity of the page.

**How it helps**:  
It allows users with low vision to examine web elements closely without losing their place or causing disorientation due to layout shifts. It's especially effective on dynamic or JavaScript-heavy sites where traditional zooming methods break usability.

**Demo**:  
![zoomer](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/zoom-lens-demo-ezgif.com-optimize.gif?raw=true)

---

### Chat Mode (Assistant)

**Purpose**:  
This feature introduces a conversational interface that lets users interact with the website by describing their intentions in plain language (e.g., "Click the submit button"). The assistant interprets these commands and performs the actions on behalf of the user.

**How it helps**:  
It removes the need for manual navigation, especially for users with motor difficulties or cognitive fatigue. Rather than manually exploring complex layouts, the user can describe what they want — and the system does it.

**Demo**:  
![AI](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/chat-mode.gif?raw=true)

---

### Agent Mode (Autonomous Navigation)

**Purpose**:  
Agent Mode is designed for users who prefer hands-free or high-level interaction. Instead of giving granular commands, users can describe tasks (e.g., "Search for the best Kaggle notebooks") and the AI agent autonomously performs the multi-step task.

**How it helps**:  
It’s ideal for users with severe disabilities, cognitive impairments, or those unfamiliar with complex interfaces. It reduces the need for repetitive actions and allows even novice users to extract meaningful content from the web.

**Demo**:  
![agent](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/agent-mode.gif?raw=true)

---

### Learner Mode

**Purpose**:  
This mode transforms the assistant into a subject-specific tutor. Users can ask educational questions (e.g., "Explain this math problem") or request historical, scientific, or conceptual explanations.

**How it helps**:  
Designed with students and curious learners in mind, especially those using accessibility tools, Learner Mode provides structured, step-by-step explanations that are easy to follow, without relying on external links or scattered web content.

**Demo**:  
![learner](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/learner-mode.gif?raw=true)

---

### Smart Text Highlight (OCR)

**Purpose**:  
This feature scans the live-rendered web page using Optical Character Recognition (OCR) and overlays highlights on recognized text. It makes visually or semantically important information stand out even if it's buried in cluttered layouts or unlabelled elements.

**How it helps**:  
It enhances readability for users who struggle with text location, font sizes, or dense designs. It’s especially helpful on poorly structured websites, inaccessible forms, or image-based content where text is not natively selectable.

**Demo**:  
![text](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/text-highlight-demo-ezgif.com-optimize.gif?raw=true)

---

### Braille Light Display

**Purpose**:  
This is an experimental feature that simulates a Braille-like interface on screen using white dots and high contrast visual cues. It works best in dark rooms with increased screen brightness and mimics Braille cell patterns through light feedback.

**How it helps**:  
It offers blind users, particularly those with some light sensitivity, a new way to receive tactile-style feedback digitally — an innovation rarely attempted in web accessibility interfaces.

**Demo**:  
![braille](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/gifs/brail-board-demo-ezgif.com-optimize.gif?raw=true)

---

## A Real-World Use Case

> Imagine you're a student with low vision and hearing loss.  
> Your teacher assigns you to study a Kaggle notebook.

- You open kaggle.com  
- You can't find the “Code” button  
- You zoom in, and the layout breaks  
- Your screen reader reads unrelated content  
- Time’s up — you haven’t started

Now imagine using **Accessweb**:

- The AI assistant clicks the button for you  
- The lens magnifies what you need — cleanly  
- Key text is highlighted automatically  
- You just describe what you want — and it’s done

> _That’s what true accessibility looks like._

---

## Architecture

![Architecture Diagram (Lucidchart)](https://github.com/AYUSHKHAIRE/web-view/blob/main/assets/pictures/gemma-3n-challenge-architecture.png?raw=true)

Accessweb is built on a full Python stack with real-time rendering and browser simulation, backed by:

- **Selenium** (for web automation and page rendering)
- **BeautifulSoup + Tesseract OCR** (for content parsing and text detection)
- **Docker** (for faster spin up)
- **Django / Django Channels / Redis  ** (backend framework and real time streaming)
- **Gemma 3n and Gemini 2.0 Falsh** (for AI-driven assistant logic and local language understanding)
- **Browser use** (for full agent mode)
- **OpenCV** (for processing visuals, screenshots, and GIFs)
- **Frontend stack**: HTML/CSS/JS for all overlays and lens interfaces
- **Concepts**: Websockets , real time streaming , threading , queue
---

## Bonus: Sign Language Classifier

🧾 [CNN for ASL Recognition (Kaggle)](https://www.kaggle.com/code/ayushkhaire/asl-cnn)

This notebook explores the use of Convolutional Neural Networks to recognize American Sign Language — a future enhancement to allow deaf users to control Accessweb with gestures.
---

## Wrapping Up

> _“I didn’t just imagine accessibility. I built it.”_

**Accessweb** is the result of a 7-month journey filled with research, coding, and lived experience. It is built by someone who deeply understands accessibility challenges — and is passionate about solving them.

This is a call to action:  
If you believe in a fairer web — join in. Test, share, contribute, or simply spread the word.

Let’s create a world where the web works for everyone.

---

## Contact

- Email: [ayushkhaire.dev@gmail.com](mailto:ayushkhaire.dev@gmail.com)  
- LinkedIn: [Ayush Khaire](https://www.linkedin.com/in/ayushkhaire/)  
- [Kaggle writeup](https://www.kaggle.com/competitions/google-gemma-3n-hackathon/writeups/the-largest-impact-changing-accessibility-forever) .

---

## Disclaimer

This is an experimental project submitted to the **Google - The Gemma 3n Impact Challenge**. Deployment is in progress. All contributions, suggestions, and feedback are welcome.

---

> Let’s break the barriers. Together.  
> **#Accessweb #Gemma3n #AccessibilityForAll**
