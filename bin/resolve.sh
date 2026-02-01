#!/bin/bash
####
# Launcher script for DaVinci Resolve (Free Version)
#
# This script sets up the necessary environment variables and launches
# DaVinci Resolve within the Flatpak sandbox.
####

set -euo pipefail

# Set Resolve configuration directories to use XDG paths
# These ensure proper sandboxed storage within the Flatpak environment
export BMD_RESOLVE_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
export BMD_RESOLVE_LICENSE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/license"
export BMD_RESOLVE_LOGS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/logs"

# Ensure required directories exist
mkdir -p "${BMD_RESOLVE_LICENSE_DIR}" "${BMD_RESOLVE_LOGS_DIR}"

# Set library path to include Resolve's bundled libraries
export LD_LIBRARY_PATH="/app/libs:${LD_LIBRARY_PATH:-}"

# Workaround for GPU detection issues on NVIDIA systems
if lspci 2>/dev/null | grep -qi nvidia || [ -d /proc/driver/nvidia ]; then
    export __NV_PRIME_RENDER_OFFLOAD=1
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
fi

# Launch Resolve with all arguments passed through
exec /app/bin/resolve "$@"
