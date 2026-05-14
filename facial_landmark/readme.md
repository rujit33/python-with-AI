# Live Facial Landmark Tracker

A real-time facial landmark tracking system built using OpenCV and Google's MediaPipe Face Mesh solution.  
The application captures webcam input, detects human faces, and renders a 3D facial mesh overlay in real-time.

---

# Overview

The system performs the following operations:

1. Accesses the computer webcam
2. Captures video frames continuously
3. Detects facial landmarks using MediaPipe Face Mesh
4. Draws a facial mesh overlay on detected faces
5. Displays FPS (Frames Per Second)
6. Runs in real-time until terminated by the user

---

# Technologies Used

## 1. OpenCV

Used for:

- webcam access
- frame capture
- image display
- rendering text
- image preprocessing

### Official Website

https://opencv.org/

---

## 2. MediaPipe

Used for:

- facial landmark detection
- real-time face mesh estimation
- tracking facial geometry

### Official Website

https://developers.google.com/mediapipe

---

# System Architecture

```text
Webcam
   ↓
OpenCV Video Capture
   ↓
Frame Processing
   ↓
MediaPipe Face Mesh Detection
   ↓
Landmark Extraction
   ↓
Mesh Rendering
   ↓
Display Output Window
```

---

# Project Structure

```text
live_face_tracker/
│
├── app.py
|
├── config.py
│
├── core/
│   ├── camera.py
│   ├── face_tracker.py
│   ├── renderer.py
│   └── utils.py
│
└── README.md
```

---

# Folder and File Explanation

## app.py

Main application entry point.

Responsibilities:

- initialize system components
- run the main loop
- coordinate modules
- manage application lifecycle

---

## config.py

Contains centralized configuration values such as:

- webcam settings
- confidence thresholds
- rendering styles
- UI settings

Benefits:

- avoids hardcoded values
- easier maintenance
- easier experimentation

---

## core/camera.py

Handles webcam operations.

Responsibilities:

- initialize webcam
- capture frames
- release resources safely

---

## core/face_tracker.py

Handles MediaPipe face mesh processing.

Responsibilities:

- initialize MediaPipe FaceMesh
- process image frames
- return facial landmarks

---

## core/renderer.py

Responsible for visualization.

Responsibilities:

- draw facial mesh
- render FPS counter
- manage visual output

---

## core/utils.py

Contains utility/helper functionality.

Current utilities:

- FPS calculation

---

# Required Dependencies

```txt
opencv-python>=4.9,<5.0
mediapipe==0.10.14
numpy
```

---

# Important MediaPipe Version Note

This project specifically uses:

```txt
mediapipe==0.10.14
```

Reason:

Newer MediaPipe versions use the newer Tasks API and no longer expose:

```python
mp.solutions
```

This project depends on the classic FaceMesh API:

```python
mp.solutions.face_mesh
```

Using newer versions may cause:

```python
AttributeError: module 'mediapipe' has no attribute 'solutions'
```

---

# Running the Application

ensure working directory is "facial_landmakr"

```powershell
cd "facial_landmark"
```

Run:

```bash
python app.py
```

---

# Controls

| Key | Action           |
| --- | ---------------- |
| Q   | Quit Application |

---

# Expected Output

When the application starts successfully:

- webcam feed opens
- face is detected
- facial mesh appears over the face
- FPS counter is displayed
- tracking updates in real-time

---

# Facial Landmark Detection

The system uses MediaPipe Face Mesh which provides:

- 468 3D facial landmarks
- real-time tracking
- optimized inference pipeline
- lightweight processing

Detected regions include:

- eyes
- eyebrows
- nose
- lips
- jawline
- facial contours

---

# FPS Counter

FPS (Frames Per Second) measures real-time performance.

Formula used:

```python
fps = 1 / (current_time - previous_time)
```

Higher FPS means smoother tracking performance.

---

# Error Handling

The system includes handling for:

## Webcam Access Failure

Example:

- webcam unavailable
- webcam already in use

---

## Frame Read Failure

Detects:

- corrupted frame capture
- disconnected camera

---

## Resource Cleanup

Application safely releases:

- webcam resources
- MediaPipe resources
- OpenCV windows

using:

- `try/finally`
- proper cleanup methods

---
