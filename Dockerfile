FROM stereolabs/zed:5.4-gl-devel-cuda12.8-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=queen
ARG UID=1000
ARG GID=1000
ARG WS_NAME=ros_ws
ARG TMUXP_CONF=tmuxp.yaml
ARG ENTRYPOINT=entrypoint.sh

ENV USERNAME=${USERNAME}
ENV WS_NAME=${WS_NAME}

# Set up locale generation to prevent env errors
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Install system dependencies, Qt XCB support, and sudo
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gnupg2 \
    sudo \
    software-properties-common \
    lsb-release \
    build-essential \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && add-apt-repository universe \
    && rm -rf /var/lib/apt/lists/*

# Add and install ROS2 Humble core and development tools from the repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update && apt-get install -y \
    python3-full \
    python3-pip \
    python-is-python3 \
    ros-humble-desktop \
    ros-dev-tools \
    tmux \
    tmuxp \
    && rm -rf /var/lib/apt/lists/*

RUN sudo rosdep init || true

# Set up non-root user, reusing existing group 1000 (zed)
RUN if getent passwd ${UID} >/dev/null 2>&1; then userdel -f $(getent passwd ${UID} | cut -d: -f1); fi \
    && if ! getent group ${GID} >/dev/null 2>&1; then groupadd --gid ${GID} ${USERNAME}; fi \
    && useradd -s /bin/bash --uid ${UID} --gid ${GID} -m ${USERNAME} \
    && mkdir -p /home/${USERNAME}/.config \
    && chown -R ${UID}:${GID} /home/${USERNAME}/.config \
    && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && usermod -aG video,plugdev ${USERNAME} \
    && chmod -R a+rX /usr/local/lib/python3.10/dist-packages/

USER ${USERNAME}
WORKDIR /home/${USERNAME}/${WS_NAME}

COPY --chown=${UID}:${GID} ./${TMUXP_CONF} /home/${USERNAME}/${WS_NAME}/tmuxp.yaml
COPY --chown=${UID}:${GID} ./colcon.meta /home/${USERNAME}/${WS_NAME}/colcon.meta
COPY --chown=${UID}:${GID} ./${ENTRYPOINT} /home/${USERNAME}/${WS_NAME}/entrypoint.sh

RUN chmod +x ./entrypoint.sh

RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc && \
    echo "if [ -f /home/${USERNAME}/${WS_NAME}/install/local_setup.bash ]; \
        then source /home/${USERNAME}/${WS_NAME}/install/local_setup.bash; \
        fi" >> /home/${USERNAME}/.bashrc && \
    echo "export DISABLE_AUTO_TITLE='true'" >> /home/${USERNAME}/.bashrc

CMD [ "sleep", "infinity" ]