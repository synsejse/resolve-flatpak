#!/bin/bash
####
# Complete installation script for DaVinci Resolve (Free Version)
#
# This script sets up the Python environment and runs the main build process.
# All build logic is handled by the resolve_builder Python package.
####

set -euo pipefail

echo "=============================================="
echo "DaVinci Resolve Flatpak Build"
echo "=============================================="

echo "Setting up Python build environment..."
python3 -m venv venv
. ./venv/bin/activate
pip3 install -q ./python

echo "Running build process..."
python3 -m resolve_builder "$@"

echo "Installing launcher script..."
install -Dm755 resolve.sh /app/bin/resolve.sh

echo "=============================================="
echo "Installation complete!"
echo "=============================================="
