# syntax=docker/dockerfile:1

FROM ubuntu:24.04 AS vaf-user
ARG TZ="Europe/Berlin"
ARG USER="eclipse"
ARG CONAN_VERSION="2.20"

ENV LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

# Install common APT packages
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    bash-completion \
    ca-certificates \
    ccache \
    clangd \
    cmake \
    clang-format \
    g++-12 \
    git \
    gdb \
    pipx \
    python3-pip \
    python3.12 \
    python3.12-venv \
    rake \
    sudo \
    ssh \
    nano \
    vim \
    emacs \
    && apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/* \
    && rm -rf /var/log/*

# Comment out and adapt the lines below to add SSL certificates if needed:
# ADD url-to-your-certificate-one /usr/local/share/ca-certificates/your-certificates-folder
# ADD url-to-your-certificate-two /usr/local/share/ca-certificates/your-certificates-folder
# RUN update-ca-certificates /usr/local/share/ca-certificates/
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Build & install SIL Kit
RUN mkdir -p /tmp/silkit \
    && git clone --recurse-submodules -j4 https://github.com/vectorgrp/sil-kit.git /tmp/silkit \
    && git -C /tmp/silkit checkout tags/v5.0.1 \
    && git -C /tmp/silkit submodule update --init --recursive \
    && mkdir /tmp/silkit/build \
    && sudo cmake -DSILKIT_BUILD_DEMOS=OFF -DSILKIT_BUILD_TESTS=OFF -DSILKIT_BUILD_DASHBOARD=OFF -DSILKIT_BUILD_STATIC=ON -S /tmp/silkit -B /tmp/silkit/build \
    && sudo cmake --build /tmp/silkit/build --target install --parallel 12 \
    # Workaround for broken installation when building statically linked libraries
    && sudo cp /tmp/silkit/build/ThirdParty/_tp_spdlog/libspdlog.a /usr/local/lib/ \
    && sudo cp /tmp/silkit/build/ThirdParty/_tp_rapidyaml/librapidyaml-static.a /usr/local/lib/ \
    && sudo cp /tmp/silkit/build/Release/libSilKit.a /usr/local/lib/ \
    && sudo rm -rf /tmp/silkit

# Create working directory and add user
RUN mkdir -p /workspaces \
    # Create a default user
    && userdel -r ubuntu \
    && useradd -m -s /bin/bash -u 1000 ${USER} --groups sudo \
    # Allow usage of sudo without password
    && echo "${USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER}_all \
    && chown -R ${USER}:${USER} /workspaces

# Switch the user
USER ${USER}
ENV PATH=/home/${USER}/.local/bin:/opt/vaf/bin:$PATH

# Install python dependencies
# install uv
ENV UV_NATIVE_TLS=true
ENV UV_TOOL_BIN_DIR="/home/${USER}/.local/bin"
# conan is installed system-wide, as it is required as a package by vaf-cli
RUN pipx install uv \
    && uv tool install conan==${CONAN_VERSION} \
    && rm -rf /home/${USER}/.cache/*

# Conan packages
RUN --mount=type=bind,source=./Container/conan,target=/tmp/conan,readwrite \
    sudo chown -R 1000:1000 /tmp/conan \
    && conan install /tmp/conan -pr:a=/tmp/conan/gcc12__x86_64-pc-linux-elf --build=missing \
    && conan cache clean "*"

# Install VAF packages
RUN --mount=type=bind,source=.,target=/tmp/repo,readwrite \
    # Workaround: rake has to be called twice as you can't run a task multiple times in the same context
    sudo chown -R 1000:1000 /tmp/repo \
    && cd /tmp/repo \
    && rake prod:install:vafcli \
    && conan cache clean "*" \
    && rm -rf ~/.cache \
    && _VAF_COMPLETE=bash_source vaf | sudo tee /usr/share/bash-completion/completions/vaf > /dev/null

# Add Demos
COPY Demo /opt/vaf/Demo
