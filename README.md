# 👗 AI Wardrobe Recommendation System
### An intelligent fashion assistant that uses computer vision to recommend based on real-time body pose detection and personal style preferences.
Quick Overview

## ✨ Features

* **Real-Time Pose Detection:** Accurately detects body landmarks (shoulders, torso) using MediaPipe & CVZone.
* **Dynamic Scaling:** Automatically resizes clothing to fit the user's distance from the camera and shoulder width.
* **Smart Alignment:** Centers the shirt on the body even when the user moves around.
* **Aspect Ratio Preservation:** Supports shirts of any shape or size without distortion.
* **Web Interface:** A modern, responsive web UI with "Glassmorphism" design.
* **Mirror Effect:** Flips the camera feed for a natural mirror-like experience.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Web Framework:** Flask
* **Computer Vision:** OpenCV (`cv2`), cvzone, MediaPipe
* **Frontend:** HTML5, CSS3 (Glassmorphism Design), JavaScript

## 📂 Project Structure

```text
Virtual-Wardrobe/
│
├── Resources/           # Contains images and assets
│   └── Shirts/          # PNG images of shirts (transparent background)
│
├── templates/
│   └── index.html       # The Frontend Web Interface
│
├── app.py               # Main Flask Application
├── README.md            # Project Documentation
└── requirements.txt     # List of dependencies
