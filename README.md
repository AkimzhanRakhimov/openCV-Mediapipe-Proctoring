# AI Proctoring System

A lightweight **computer vision proctoring system** that detects suspicious behavior during exams using a webcam.
The system analyzes **head pose and eye gaze direction** in real time to detect potential cheating and generates a **JSON report** of violations.

It is built with:

* **Python**
* **OpenCV**
* **MediaPipe Face Mesh**
* **NumPy**

The system can run on a **webcam, video file, or remote camera stream**.

---

# Features

* Real-time **face tracking**
* **Head pose estimation** using `solvePnP`
* **Gaze direction detection**
* Detection of suspicious behaviors:

  * Looking left
  * Looking right
  * Looking up
  * Looking down
  * Turning head
* **Blink-aware detection** to avoid false positives
* Configurable **detection window and thresholds**
* Automatic **JSON violation report generation**
* FPS counter for performance monitoring

---

# How It Works

The system processes a video stream frame-by-frame:

1. **Face Detection**

   * MediaPipe FaceMesh detects facial landmarks.

2. **Head Pose Estimation**

   * Uses selected landmarks and a 3D face model.
   * OpenCV `solvePnP` estimates rotation vectors.
   ![Demonstration](Adobe-Express-Proctoring-2026-03-16-14-07-29.gif)

3. **Gaze Detection**

   * Calculates iris position relative to eye centers.
   * Determines gaze direction.
   ![Demonstration](Adobe-Express-Proctoring-2026-03-16-14-09-11.gif)

4. **Violation Tracking**

   * `CheatTracker` monitors the percentage of suspicious frames.
   * If the threshold is exceeded within a time window, a violation is recorded.

5. **Report Generation**

   * Violations are saved to a JSON file with timestamp and reason.

---

# Project Structure

```
.
├── main.py
├── config.py
├── CheatTrackers.py
├── head_pose_estimation.py
├── gaze_detection.py
├── helpers.py
└── report.json
```

### main.py

Main program.
Handles video input, MediaPipe processing, and integrates all modules.

### config.py

Default configuration values.

### head_pose_estimation.py

Estimates **head orientation** using OpenCV `solvePnP`.

### gaze_detection.py

Detects **eye gaze direction** using iris and eye landmarks.

### CheatTrackers.py

Tracks violations across time windows and writes reports.

### helpers.py

Utility functions:

* FPS calculation
* Saving JSON reports

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/ai-proctoring-system.git
cd ai-proctoring-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Usage

Run the system:

```bash
python main.py
```

You can also pass parameters:

```bash
python main.py \
  --video_source 0 \
  --output_file report.json \
  --detection_window 3 \
  --detection_threshold 0.3
```

---

# Parameters

| Parameter             | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `video_source`        | Webcam index, video file, or remote stream                   |
| `output_file`         | JSON file where violations are stored                        |
| `detection_window`    | Time window (seconds) used for violation analysis            |
| `detection_threshold` | Percentage of suspicious frames required to trigger a report |

Default values are defined in `config.py`.

---

# Example Output

Example `report.json`:

```json
[
  {
    "Relation of banned frames": 0.41,
    "Period": 4,
    "Reason": "Looking Right",
    "Date": "2026-03-15 18:21:03"
  }
]
```

---

# Detection Logic

A violation is reported when:

```
banned_frames / total_frames > detection_threshold
```

within the configured **detection window**.

This helps prevent false positives caused by:

* natural eye movement
* blinking
* short head movement

---

# Limitations

* Works best with **good lighting**
* Requires the **face to be visible**
* Accuracy depends on **camera quality and angle**
* Single-person use (multiple faces not fully supported)

---

# Future Improvements

Possible extensions:

* Multiple face tracking
* Deep learning gaze estimation
* Suspicious object detection (phones, books)
* Audio monitoring
* Web dashboard for reports
* Model calibration per user

---

# License

MIT License
