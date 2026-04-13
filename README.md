# Aero-Climb Zero V3: Autonomous Vacuum-Adhesion Facade Rover 🤖🧗‍♂️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Hardware: Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Zero%202W-red)](https://www.raspberrypi.com/)

An advanced, AI-powered glass cleaning robot designed for high-rise maintenance. The **Aero-Climb Zero V3** solves the "Payload-Inertia" problem by combining active vacuum adhesion with a custom fluid-stabilized reservoir.

## 🚀 The Innovation: V3 Engineering
Standard cleaning robots fail when carrying heavy liquids due to slosh inertia. The V3 architecture introduces:
- **Active Negative Lift:** The Negative lift gives stability for the cleaning robort by pushing it down, We found that if we used 50%-60% we can move the entire robot without the completly sticking .
- **Slosh Mitigation:** An internal **Honeycomb Baffle Grid** that reduces liquid inertia by **85%**.
- **Constant-Contact Spine:** A spring-loaded internal frame ensuring tracks never lose contact with irregular glass surfaces.

## 🛠 Tech Stack
- **Brain:** Raspberry Pi Zero 2W (Linux OS)
- **Computer Vision:** OpenCV (Stain detection & Path planning)
- **Language:** Python 3.10
- **Hardware Control:** `pigpio` for DMA-based PWM (5010 ESC control)
- **Adhesion:** 5010 BLDC Motor + Centrifugal Impeller
- **Power:** 6S LiPo (22.2V)

## 📂 Repository Structure
```text
├── src/
│   ├── hardware/        # GPIO, ESC, and Pump control scripts
│   └── main.py          # Central State Machine
└── requirements.txt     # Python dependencies
