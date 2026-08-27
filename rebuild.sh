#!/bin/bash
set -e

sudo mkdir -p /home/${USERNAME}/.ros
sudo chown -R ${USERNAME}: /home/${USERNAME}/.ros

sudo apt-get update
rosdep update --rosdistro=humble
rosdep install --from-paths ./src --ignore-src -r -y
sudo rm -rf /var/lib/apt/lists/*

colcon build \
    --meta colcon.meta \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo

source /opt/ros/humble/setup.bash
source /home/${USERNAME}/${WS_NAME}/install/local_setup.bash
# TODO: write tmuxp config and load it here, split rebuild and entrypoint into separate scripts