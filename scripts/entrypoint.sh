#!/bin/bash

# This script is executed when the container starts.
# It checks DEPLOYMENT environment variable and runs the appropriate command.

set -e

# Basic health check
if [ ! -f /usr/src/app/app/main.py ]; then
    echo "Error: main.py not found!"
    exit 1
fi

echo "Starting entrypoint script..."
echo "DEPLOYMENT=$DEPLOYMENT"

if [ "$DEPLOYMENT" = "web" ]; then
    echo "Running in web mode..."
    exec python -m chainlit run app/main.py
elif [ "$DEPLOYMENT" = "local" ]; then
    echo "Running in local mode..."
    exec sh scripts/install_datalayer.sh;  python -m chainlit run app/main.py; 
else
    echo "Running in development mode..."
    exec sleep infinity
fi
