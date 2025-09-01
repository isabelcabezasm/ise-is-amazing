# Use Microsoft dev container base image
FROM mcr.microsoft.com/devcontainers/base:jammy AS base

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set up basic environment
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspaces/ui-prototyper

# Install additional system dependencies if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-extra \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# The base image already includes:
# - A non-root user (vscode)
# - Git
# - Common development tools
# - Sudo access for the vscode user

# Set the working directory
WORKDIR /workspaces/ui-prototyper

# Default command
CMD ["/bin/bash"]
