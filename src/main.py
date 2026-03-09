import cv2
import numpy as np
import pigpio
import threading
import time

# --- GPIO PIN CONFIGURATION (L298N Dual Channel) ---
VACUUM_ESC_PIN = 18
PUMP_RELAY_PIN = 17

# Left Track
LEFT_PWM = 12
LEFT_IN1 = 22
LEFT_IN2 = 27 
# Right Track
RIGHT_PWM = 13
RIGHT_IN1 = 23
RIGHT_IN2 = 24

# --- CONSTANTS ---
VAC_ARM = 1000
VAC_MIN_GRIP = 1450 # Increased for safety during turns
CRACK_THRESHOLD = 2000 # Sensitivity for edge detection

class AeroClimbV4:
    def __init__(self):
        self.pi = pigpio.pi()
        self.setup_gpio()
        self.arm_esc()
        
        self.is_running = True
        self.dirt_detected = False
        self.danger_detected = False # Cracks/Edges
        
    def setup_gpio(self):
        for pin in [PUMP_RELAY_PIN, LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2]:
            self.pi.set_mode(pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(LEFT_PWM, 800)
        self.pi.set_PWM_frequency(RIGHT_PWM, 800)

    def arm_esc(self):
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_ARM)
        time.sleep(2)

    # --- UPDATED VISION: CRACK & DIRT DETECTION ---
    def vision_engine(self):
        cap = cv2.VideoCapture(0)
        while self.is_running:
            ret, frame = cap.read()
            if not ret: continue
            
            # 1. Crack/Edge Detection (Canny)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # If too many "edges" are in the path, it's a crack or the frame
            edge_score = cv2.countNonZero(edges[50:150, :]) 
            self.danger_detected = edge_score > CRACK_THRESHOLD

            # 2. Dirt Detection (Same as before)
            _, thresh = cv2.threshold(gray[100:200, 50:270], 100, 255, cv2.THRESH_BINARY_INV)
            self.dirt_detected = cv2.countNonZero(thresh) > 5000
            
            time.sleep(0.03)
        cap.release()

    # --- OMNIDIRECTIONAL MOVEMENT ---
    def drive(self, left_speed, right_speed):
        """Supports forward, backward, and tank turns."""
        # Left Motor Logic
        self.pi.write(LEFT_IN1, 1 if left_speed >= 0 else 0)
        self.pi.write(LEFT_IN2, 0 if left_speed >= 0 else 1)
        self.pi.set_PWM_dutycycle(LEFT_PWM, abs(left_speed))
        
        # Right Motor Logic
        self.pi.write(RIGHT_IN1, 1 if right_speed >= 0 else 0)
        self.pi.write(RIGHT_IN2, 0 if right_speed >= 0 else 1)
        self.pi.set_PWM_dutycycle(RIGHT_PWM, abs(right_speed))

    def control_loop(self):
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_MIN_GRIP)
        time.sleep(1)
        
        while self.is_running:
            # SAFETY FIRST: If a crack or edge is detected, STOP and BACK UP
            if self.danger_detected:
                print("DANGER: Crack/Edge detected! Reversing...")
                self.pi.write(PUMP_RELAY_PIN, 0)
                self.drive(-100, -100) # Back up
                time.sleep(1)
                self.drive(150, -150)  # Spin 90 degrees to find a new path
                time.sleep(0.8)
                continue

            # NORMAL OPERATION
            if self.dirt_detected:
                self.pi.write(PUMP_RELAY_PIN, 1)
                self.drive(80, 80) # Slow scrub
            else:
                self.pi.write(PUMP_RELAY_PIN, 0)
                self.drive(160, 160) # Fast cruise
            
            time.sleep(0.1)

    def shutdown(self):
        self.is_running = False
        self.drive(0, 0)
        self.pi.write(PUMP_RELAY_PIN, 0)
        # Hold suction for 2 seconds while user grabs it
        time.sleep(2) 
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_ARM)
        self.pi.stop()
        
