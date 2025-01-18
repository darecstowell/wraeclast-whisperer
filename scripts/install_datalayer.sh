#!/bin/bash

# This script installs the Chainlit datalayer and runs the necessary migrations.
# It downloads node, the repository, extracts repo, runs the necessary commands and cleans up.

# Exit immediately if a command exits with a non-zero status
set -e

# Define the repository URL
REPO_URL="https://github.com/Chainlit/chainlit-datalayer/archive/refs/heads/main.zip"

# Define the directory to extract the repository into
TARGET_DIR="/usr/src/app/chainlit-datalayer"

# Function to handle errors
error_exit() {
    echo "Error: $1"
    exit 1
}

# Install Node.js and npm
echo "Installing Node.js and npm..."
apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt-get install -y nodejs \
    && apt-get install -y unzip \
    && node -v || error_exit "Failed to install Node.js and npm."

# Check if the target directory already exists and is not empty
if [ -d "$TARGET_DIR" ] && [ "$(ls -A $TARGET_DIR)" ]; then
    echo "Repository already installed at $TARGET_DIR."
else
    # Download the repository as a ZIP file
    wget -O repo.zip $REPO_URL || error_exit "Failed to download repository."

    # Create the target directory if it doesn't exist
    mkdir -p $TARGET_DIR || error_exit "Failed to create target directory."

    # Extract the ZIP file into the target directory
    unzip repo.zip -d $TARGET_DIR || error_exit "Failed to extract ZIP file."

    echo "Repository installed at $TARGET_DIR."
fi

# Navigate to the target directory
cd $TARGET_DIR/chainlit-datalayer-main || error_exit "Failed to navigate to target directory."

# Run npx prisma migrate deploy with auto yes
yes | npx prisma migrate deploy || error_exit "Failed to run npx prisma migrate deploy."

# Clean up
cd ../../
rm repo.zip || true
rm -rf $TARGET_DIR/chainlit-datalayer || true

# Uninstall Node.js and npm
echo "Cleaning up Node.js and npm..."
apt-get remove --purge -y nodejs npm \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f nodesource_setup.sh \
    && rm package-lock.json || true \
    && rm package.json || true

echo "Chainlit datalayer installed and migrations deployed successfully."
