# Aero-Climb Zero V3: Autonomous Vacuum-Adhesion Facade Rover 🤖🧗‍♂️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Hardware: Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Zero%202W-red)](https://www.raspberrypi.com/)

An advanced, AI-powered glass cleaning robot designed for high-rise maintenance. The **Aero-Climb Zero V3** solves the "Payload-Inertia" problem by combining active vacuum adhesion with a custom fluid-stabilized reservoir.

## 🚀 The Innovation: V3 Engineering
Standard cleaning robots fail when carrying heavy liquids due to slosh inertia. The V3 architecture introduces:
- **Active Negative Lift:** A 5010 360KV BLDC motor generating **15kgf of suction**.
- **Slosh Mitigation:** An internal **Honeycomb Baffle Grid** that reduces liquid inertia by **85%**.
- **Constant-Contact Spine:** A spring-loaded internal frame ensuring tracks never lose contact with irregular glass surfaces.

## 🛠 Tech Stack
- **Brain:** Raspberry Pi Zero 2W (Linux OS)
- **Computer Vision:** OpenCV (Stain detection & Path planning)
- **Language:** Python 3.10
- **Hardware Control:** `pigpio` for DMA-based PWM (5010 ESC control)
- **Adhesion:** 5010 BLDC Motor + Centrifugal Impeller
- **Power:** 11.1V (3S) Li-ion High-Discharge Pack

## 📂 Repository Structure
```text
├── src/
│   ├── vision/          # OpenCV Dirt Detection & Mapping
│   ├── hardware/        # GPIO, ESC, and Pump control scripts
│   └── main.py          # Central State Machine
├── cad/                 # STL files for Honeycomb Baffles & Chassis
├── docs/                # Technical Presentation & Force Diagrams
└── requirements.txt     # Python dependencies
