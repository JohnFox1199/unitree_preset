# Unitree G1 Simulation Preset

Complete simulation environment for Unitree G1 humanoid robot using MuJoCo physics engine.

## 📋 Contents

- `unitree_mujoco/` - MuJoCo models and simulation environments for G1 robot
- `unitree_sdk2/` - C++ SDK for Unitree robots
- `unitree_sdk2_python/` - Python bindings for Unitree SDK
- `requirements.txt` - Python dependencies list

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
