# Beetle AutoCar - Setup & Usage Guide

## Prerequisites

The ZED SDK requires:
- Docker
- NVIDIA GPU with latest drivers
- NVIDIA Container Runtime

Please refer the [NVIDIA Container Runtime documentation](https://github.com/NVIDIA/nvidia-container-runtime) to ensure these are installed on your system.

---

## Getting Started

### 1. Clone the Repository

**Option A: Clone directly**
```bash
git clone --recurse-submodule https://github.com/AviralxD/beetle-autocar.git
```

**Option B: Fork it first (preferred)**
```bash
git clone --recurse-submodule https://github.com/<your-username>/beetle-autocar.git
```

### 2. Build the Docker Container

```bash
cd beetle-autocar/
docker compose up -d --build
```

**To run/restart the container (without rebuilding) drop the --build tag from the command**

### 3. Attaching to the Container

```bash
docker exec -it beetle-zed /bin/bash
```

**For attaching via vscode use the Dev Containers extension to attach to the running container**

---

## Building the ROS2 Workspace

Run the entrypoint script (named rebuild.sh in the repo) within the container to update deps and rebuild the project:

```bash
./entrypoint.sh
```

**Note:** The build script automatically sources the workspace

## Running controller teleop
Ensure you've built and sourced the beetle_zed package

```bash
colcon build --packages-select beetle_zed --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo
source /home/queen/beetle_ws/install/setup.bash
ros2 launch beetle_zed teleop.launch.py serial_port:=/dev/ttyACM0
```
**Note:** The build script automatically sources the workspace

Hold the controller's deadman button (LB by default) to enable teleop. \
Use `throttle_axis`, `steering_axis`, `deadman_button`, `serial_port`, and
`baud_rate` launch arguments to match the microcontroller and gamepad.

---