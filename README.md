# ARGUS: AI-Powered Digital Invigilator System

ARGUS (Automated Remote Guardian for Ubiquitous Supervision) is an intelligent proctoring system designed to ensure exam integrity through real-time behavioral analysis and identity verification.

## 🚀 Features

### 1. Identity & Liveness Verification
*   **Face Matching**: Uses **InsightFace** (`buffalo_l`) to match the person in the frame against a registered reference photo with high precision.
*   **Anti-Spoofing (Blink Detection)**: Utilizes **MediaPipe** Face Mesh to calculate the **Eye Aspect Ratio (EAR)**. It flags a "FAKE/SPOOF" status if the user fails to blink within a specified temporal threshold, preventing the use of static photos.

### 2. Behavioral Monitoring & Gaze Tracking
*   **Attention Monitoring**: Monitors the iris position relative to the eye corners to detect if the examinee is looking away from the screen (Looking Left/Right) or maintaining a "FOCUSED" state.
*   **Head Pose Estimation**: Analyzes head orientation to flag suspicious movements.

### 3. Object Detection (Module 2)
*   **Restricted Detection**: Module 2 functions as a specialized object detector (e.g., for mobile phones, books, or multiple people in the frame).
*   **Runtime Deployment**: The specific weights and restricted detection files are added at runtime to maintain security and modularity.
*   *Note: Early versions of this project utilized YOLOv8 for detection before transitioning to a more customized implementation for specific proctoring requirements.*

## 🛠️ Technology Stack
*   **Core Logic**: Python
*   **Computer Vision**: OpenCV
*   **Artificial Intelligence**: InsightFace, MediaPipe
*   **Deep Learning (Legacy)**: YOLOv8 (Explored in early development)
*   **GUI**: Tkinter

## 📋 Installation & Usage

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install opencv-python mediapipe numpy insightface pillow
   ```
3. Run the main engine:
   ```bash
   python "Module 1/ARGUS-1.py"
   ```

## 🛡️ Anti-Cheating Logic
*   **Liveness Bar**: A visual timer that resets every time a blink is detected.
*   **ID Match Status**: Prevents impersonation by continuously verifying the user's facial embedding against the registration.
*   **Environmental Integrity**: Module 2 monitors for restricted objects and unauthorized secondary persons.

---
**Developed by Muhammad Kaif**
