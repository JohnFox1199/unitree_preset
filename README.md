# Unitree G1 Simulation Preset

Complete simulation environment for Unitree G1 humanoid robot using MuJoCo physics engine.

## 📋 Contents

- `unitree_mujoco/` - MuJoCo models and simulation environments for G1 robot
- `unitree_sdk2/` - C++ SDK for Unitree robots  
- `unitree_sdk2_python/` - Python bindings for Unitree SDK
- `requirements.txt` - Python dependencies list

## 📦 Verified Software Versions

### Core System
- **Ubuntu**: 22.04.5 LTS
- **Python**: 3.10.12
- **GCC**: 11.4.0
- **CMake**: 3.22.1
- **Git**: 2.34.1

### Physics & Simulation
- **MuJoCo**: 3.3.6
- **mujoco-py**: 2.1.2.14
- **OpenCV**: 4.8.1.78
- **PyBullet**: 3.2.5 (optional)

### Python Core Libraries
- **numpy**: 1.26.4
- **scipy**: 1.11.4
- **matplotlib**: 3.8.3
- **torch**: 2.1.2 (CPU version)

### Robotics & Control
- **gym**: 0.21.0
- **transforms3d**: 0.4.1
- **quaternion**: 2023.8.25
- **rospkg**: 1.5.0
- **unitree_sdk2py**: 1.0.0 (from source)

### Utility Libraries
- **Pillow**: 10.1.0
- **imageio**: 2.33.1
- **imageio-ffmpeg**: 0.4.9
- **pyyaml**: 6.0.1
- **Jupyter**: 1.0.0

## 🚀 Quick Start

### Prerequisites

**Ubuntu 22.04** is recommended. Install system dependencies:

```bash
sudo apt update && sudo apt install -y \
    git wget curl tar \
    build-essential cmake make g++ \
    python3 python3-pip python3-venv python3-dev \
    libgl1-mesa-dev libglfw3 patchelf libglew-dev \
    libosmesa6-dev libegl1-mesa-dev \
    libopencv-dev portaudio19-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libboost-all-dev
