import cv2
import numpy as np
import pigpio
import threading
import time

# --- GPIO PIN CONFIGURATION ---
VACUUM_ESC_PIN = 18    # 5010 BLDC ESC (Needs PWM)
PUMP_RELAY_PIN = 17    # Water Pump
# L298N Track Motors
LEFT_TRACK_PWM = 12    
LEFT_DIR_1 = 22
RIGHT_TRACK_PWM = 13
RIGHT_DIR_1 = 23

# --- CONSTANTS ---
VAC_ARM = 1000         # Min PWM for ESC arming
VAC_MIN_GRIP = 1400    # Minimum speed to stay on glass
VAC_CLEAN_SPEED = 1750 # High speed for heavy 10L load
STAIN_THRESHOLD = 5000 # Pixel count to trigger spray

class AeroClimbV3:
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit("Error: pigpiod not running!")
            
        # Initialize Hardware
        self.setup_gpio()
        self.arm_esc()
        
        self.is_running = True
        self.dirt_detected = False
        self.current_frame = None

    def setup_gpio(self):
        # Set modes
        self.pi.set_mode(PUMP_RELAY_PIN, pigpio.OUTPUT)
        self.pi.set_mode(LEFT_DIR_1, pigpio.OUTPUT)
        self.pi.set_mode(RIGHT_DIR_1, pigpio.OUTPUT)
        # Setup PWM frequencies (800Hz for motors, 50Hz for ESC)
        self.pi.set_PWM_frequency(LEFT_TRACK_PWM, 800)
        self.pi.set_PWM_frequency(RIGHT_TRACK_PWM, 800)

    def arm_esc(self):
        print("Arming 5010 Vacuum Motor...")
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_ARM)
        time.sleep(2)
        print("Vacuum Ready.")

    # --- VISION THREAD ---
    def vision_engine(self):
        cap = cv2.VideoCapture(0) # Pi Camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        while self.is_running:
            ret, frame = cap.read()
            if not ret: continue
            
            # Image Processing: Detect Stains
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Focus on the 'Cleaning Path' ROI
            roi = gray[100:200, 50:270] 
            _, thresh = cv2.threshold(roi, 100, 255, cv2.THRESH_BINARY_INV)
            
            dirt_score = cv2.countNonZero(thresh)
            self.dirt_detected = dirt_score > STAIN_THRESHOLD
            self.current_frame = frame
            
            time.sleep(0.05)
        cap.release()

    # --- HARDWARE CONTROL METHODS ---
    def set_movement(self, speed, direction="FORWARD"):
        # L298N Logic
        dir_val = 1 if direction == "FORWARD" else 0
        self.pi.write(LEFT_DIR_1, dir_val)
        self.pi.write(RIGHT_DIR_1, dir_val)
        self.pi.set_PWM_dutycycle(LEFT_TRACK_PWM, speed)
        self.pi.set_PWM_dutycycle(RIGHT_TRACK_PWM, speed)

    def control_loop(self):
        # Initial Adhesion
        print("Engaging Vacuum Adhesion...")
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_MIN_GRIP)
        time.sleep(1) # Wait for pressure to build
        
        while self.is_running:
            # 1. Vacuum Speed Management (Increase if heavy load detected)
            self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_CLEAN_SPEED)

            # 2. Targeted Cleaning Logic
            if self.dirt_detected:
                # Active Cleaning Mode
                self.pi.write(PUMP_RELAY_PIN, 1) # Start Pump
                self.set_movement(80)            # Slower for scrubbing
            else:
                self.pi.write(PUMP_RELAY_PIN, 0) # Stop Pump
                self.set_movement(150)           # Cruise speed
            
            time.sleep(0.1)

    def shutdown(self):
        print("\nShutting Down Safely...")
        self.is_running = False
        self.pi.write(PUMP_RELAY_PIN, 0)
        self.set_movement(0)
        # Slowly ramp down vacuum to prevent sudden drop
        self.pi.set_servo_pulsewidth(VACUUM_ESC_PIN, VAC_ARM)
        time.sleep(1)
        self.pi.stop()

# --- EXECUTION ---
if __name__ == "__main__":
    robot = AeroClimbV3()
    
    # Start Threads
    t1 = threading.Thread(target=robot.vision_engine)
    t2 = threading.Thread(target=robot.control_loop)
    
    t1.start()
    t2.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        robot.shutdown()
        t1.join()
        t2.join()
