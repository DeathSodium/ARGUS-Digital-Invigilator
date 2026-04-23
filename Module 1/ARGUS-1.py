import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import math


# --- CHECK FOR INSIGHTFACE ---
try:
    from insightface.app import FaceAnalysis
except ImportError:
    print("CRITICAL: InsightFace not installed.")
    exit()

#from scipy.spatial import distance as dist

class argus:
    def __init__(self):
        # --- CONFIGURATION ---
        self.EAR_THRESHOLD = 0.21       # Blink sensitivity
        self.VERIFY_INTERVAL = 2.0      # Face ID check interval
        self.LIVENESS_THRESHOLD = 15.0  # Seconds without blink before flagging FAKE
        
        # --- COMPONENTS ---
        print("[INIT] Loading MediaPipe...")
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        print("[INIT] Loading InsightFace...")
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        # --- STATE ---
        self.reference_embedding = None
        self.face_match = True 
        self.blink_count = 0
        self.last_blink_time = time.time() # Timer for liveness
        
        self.running = True
        self.frame_buffer = None
        self.lock = threading.Lock()
        self.last_verify_time = 0

    def get_ear(self, eye_landmarks, w, h):
    # Convert points to numpy arrays for vector subtraction
        p1 = np.array(eye_landmarks[1])
        p5 = np.array(eye_landmarks[5])
        p2 = np.array(eye_landmarks[2])
        p4 = np.array(eye_landmarks[4])
        p0 = np.array(eye_landmarks[0])
        p3 = np.array(eye_landmarks[3])

    # Calculate distances using Linear Algebra Norm (L2 Norm)
        A = np.linalg.norm(p1 - p5)
        B = np.linalg.norm(p2 - p4)
        C = np.linalg.norm(p0 - p3)
    
        return (A + B) / (2.0 * C)

    def get_iris_position(self, iris_center, right_point, left_point):
        center_to_right = np.linalg.norm(iris_center - right_point)
        total_width = np.linalg.norm(right_point - left_point)
        return center_to_right / total_width

    def verify_identity_worker(self):
        while self.running:
            if self.reference_embedding is None:
                time.sleep(0.1)
                continue
                
            with self.lock:
                current_frame_copy = None
                if self.frame_buffer is not None:
                    current_frame_copy = self.frame_buffer.copy()
            
            if current_frame_copy is not None and (time.time() - self.last_verify_time > self.VERIFY_INTERVAL):
                try:
                    faces = self.app.get(current_frame_copy)
                    if len(faces) > 0:
                        curr_emb = faces[0].embedding
                        sim = np.dot(self.reference_embedding, curr_emb) / (np.linalg.norm(self.reference_embedding) * np.linalg.norm(curr_emb))
                        self.face_match = sim > 0.35 
                        self.last_verify_time = time.time()
                except Exception:
                    pass
            time.sleep(0.1)

    def register_user(self, cap):
        print("\n>> REGISTRATION: Look at camera and press 'SPACE' <<")
        while True:
            ret, frame = cap.read()
            if not ret: continue
            
            h, w, _ = frame.shape
            cv2.rectangle(frame, (w//2-100, h//2-100), (w//2+100, h//2+100), (0, 255, 0), 2)
            cv2.putText(frame, "Press SPACE to Register", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Registration', frame)
            key = cv2.waitKey(1)
            
            if key == 32: # SPACE
                faces = self.app.get(frame)
                if len(faces) != 1:
                    print("Error: Detect exactly ONE face.")
                    continue
                
                self.reference_embedding = faces[0].embedding
                self.last_blink_time = time.time() # Reset timer on start
                cv2.destroyWindow('Registration')
                return True
            elif key == ord('q'):
                return False

    def run(self):
        cap = cv2.VideoCapture(1) 
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        if not self.register_user(cap):
            cap.release()
            return

        t = threading.Thread(target=self.verify_identity_worker, daemon=True)
        t.start()

        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        
        while True:
            ret, frame = cap.read()
            if not ret: break

            h, w, c = frame.shape
            
            with self.lock:
                self.frame_buffer = frame

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            status_text = "FOCUSED"
            status_color = (0, 255, 0)
            liveness_status = "LIVE"
            liveness_color = (0, 255, 0)

            # --- LIVENESS TIMER CHECK ---
            time_since_blink = time.time() - self.last_blink_time
            
            if time_since_blink > self.LIVENESS_THRESHOLD:
                liveness_status = "FAKE / SPOOF (NO BLINK)"
                liveness_color = (0, 0, 255) # RED
            elif time_since_blink > (self.LIVENESS_THRESHOLD - 3):
                liveness_status = "WARNING: BLINK NOW"
                liveness_color = (0, 165, 255) # ORANGE

            if results.multi_face_landmarks:
                mesh_points = np.array([np.multiply([p.x, p.y], [w, h]).astype(int) for p in results.multi_face_landmarks[0].landmark])
                
                # 1. BLINK DETECTION (Reset Timer)
                ear = self.get_ear(mesh_points[LEFT_EYE], w, h)
                if ear < self.EAR_THRESHOLD:
                    self.blink_count += 1
                    self.last_blink_time = time.time() # <--- RESET TIMER HERE
                    cv2.putText(frame, "BLINK", (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # 2. GAZE
                iris_center = mesh_points[468] 
                right_point = mesh_points[33]
                left_point = mesh_points[133]
                ratio = self.get_iris_position(iris_center, right_point, left_point)
                
                if ratio < 0.40:
                    status_text = "LOOKING RIGHT"
                    status_color = (0, 0, 255)
                elif ratio > 0.60:
                    status_text = "LOOKING LEFT"
                    status_color = (0, 0, 255)
                    
                cv2.circle(frame, tuple(iris_center), 3, (0, 255, 255), -1)

            else:
                liveness_status = "NO FACE"
            
            # --- UI DRAWING ---
            # Liveness Bar (Visual Timer)
            bar_width = int((min(time_since_blink, self.LIVENESS_THRESHOLD) / self.LIVENESS_THRESHOLD) * 200)
            cv2.rectangle(frame, (20, 100), (20 + bar_width, 110), liveness_color, -1)
            cv2.rectangle(frame, (20, 100), (220, 110), (255, 255, 255), 1)
            
            cv2.putText(frame, f"Liveness: {liveness_status}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, liveness_color, 2)
            cv2.putText(frame, f"Gaze: {status_text}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            
            id_text = "MATCH" if self.face_match else "UNKNOWN"
            id_color = (0, 255, 0) if self.face_match else (0, 0, 255)
            cv2.putText(frame, f"ID: {id_text}", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, id_color, 2)

            cv2.imshow("ARGUS", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    argus().run()