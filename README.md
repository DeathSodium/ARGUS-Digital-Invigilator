# ARGUS: AI-Powered Digital Invigilator System

ARGUS (Automated Remote Guardian for Ubiquitous Supervision) is an intelligent proctoring system designed to ensure exam integrity through real-time behavioral analysis and identity verification.

## 🚀 Features

### 1. Identity & Liveness Verification
*   **Face Matching**: Uses **InsightFace** (`buffalo_l`) to match the person in the frame against a registered reference photo with high precision.
*   **Anti-Spoofing (Blink Detection)**: Utilizes **MediaPipe** Face Mesh to calculate the **Eye Aspect Ratio (EAR)**. It flags a "FAKE/SPOOF" status if the user fails to blink within a specified temporal threshold, preventing the use of static photos.

### 2. Behavioral Monitoring
*   **Gaze Tracking**: Monitors the iris position relative to the eye corners to detect if the examinee is looking away from the screen (Looking Left/Right).
*   **Attention Monitoring**: Real-time feedback on "FOCUSED" vs "UNFOCUSED" states.

### 3. Modular Architecture
*   **Module 1**: Core proctoring engine with face verification and liveness detection.
*   **Module 2**: GUI-based classification tool for custom behavior training and recognition.

## 🛠️ Technology Stack
*   **Core Logic**: Python
*   **Computer Vision**: OpenCV
*   **Face Analysis**: InsightFace (Sub-module)
*   **Landmark Detection**: MediaPipe
*   **Numerical Processing**: NumPy
*   **GUI**: Tkinter (Module 2)

## 📋 Installation & Usage

### Prerequisites
*   Python 3.8+
*   Webcam

### setup
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

---
*Developed as an AI Lab Project | Semester 5*
