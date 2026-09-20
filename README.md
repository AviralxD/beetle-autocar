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

---

## Running SLAM w rviz2
Ensure you've built the beetle_zed package
```bash
colcon build --packages-select beetle_zed --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo
source /home/queen/beetle_ws/install/setup.bash
ros2 launch beetle_zed slam.launch.py
```

**Note:** The build script automatically sources the workspace

---