"""
Setup utilities for DaVinci Resolve Flatpak installation.

This module handles extracting the DaVinci Resolve installer and setting up all
necessary files and directories within the Flatpak application prefix.

This script leverages heavily on work from makeresolvedeb, with great thanks:
https://www.danieltufvesson.com/makeresolvedeb
"""

import glob
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from resolve_builder.constants import BuildConfig

PREFIX = Path("/app")
DESKTOP_DIR = Path("desktop")


def run_command(
    cmd: list[str], check: bool = True
) -> subprocess.CompletedProcess[bytes]:
    """Run a shell command and return the result."""
    print(f"  Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=False)


def create_directory(path: str | Path, mode: int = 0o755) -> None:
    """Create a directory with the specified permissions."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, mode)


def setup_directories() -> None:
    """Create the required directory structure for DaVinci Resolve."""
    print("Creating metainfo directory structure...")

    directories = [
        "/app/share/metainfo",
    ]

    for directory in directories:
        try:
            create_directory(directory)
            print(f"  Created: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}", file=sys.stderr)
            sys.exit(1)

    print("Directory structure created successfully.")


def fix_permissions(path: Path) -> None:
    """
    Fix permissions on extracted files.

    Matches the original behavior: `chmod a+r,u+w` for files and `chmod a+rx,u+w` for dirs.
    This adds read/write permissions without removing existing execute bits.
    """
    print("Fixing permissions...")
    for root, dirs, files in os.walk(path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            current_mode = os.stat(dir_path).st_mode
            new_mode = current_mode | 0o555 | 0o200
            os.chmod(dir_path, new_mode)
        for f in files:
            file_path = os.path.join(root, f)
            current_mode = os.stat(file_path).st_mode
            new_mode = current_mode | 0o444 | 0o200
            os.chmod(file_path, new_mode)


def create_directory_structure() -> None:
    """Create required directory structure."""
    print("Creating directory structure...")
    directories = [
        PREFIX / "easyDCP",
        PREFIX / "scripts",
        PREFIX / "share",
        PREFIX / "Fairlight",
        PREFIX / "share" / "applications",
        PREFIX / "share" / "icons" / "hicolor" / "128x128" / "apps",
        PREFIX / "share" / "icons" / "hicolor" / "256x256" / "apps",
        PREFIX / "Apple Immersive" / "Calibration",
        PREFIX / "Extras",
        PREFIX / "share" / "metainfo",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o755)


def copy_tree(src: Path, dst: Path) -> None:
    """Copy a directory tree, preserving symlinks and permissions."""
    if src.exists():
        shutil.copytree(
            src, dst, symlinks=True, dirs_exist_ok=True, copy_function=shutil.copy2
        )


def copy_file(src: Path, dst: Path) -> None:
    """Copy a single file."""
    if src.exists():
        shutil.copy2(src, dst)


def remove_conflicting_libraries(libs_path: Path) -> None:
    """
    Remove conflicting GLib libraries.

    This resolves undefined symbol errors with libpango.
    See: https://www.reddit.com/r/Fedora/comments/12z32r1/davinci_resolve_libpango_undefined_symbol_g/
    """
    print("Removing conflicting GLib libraries...")
    patterns = ["libglib*", "libgio*", "libgmodule*", "libgobject*"]
    for pattern in patterns:
        for lib_file in libs_path.glob(pattern):
            lib_file.unlink()
            print(f"  Removed: {lib_file.name}")


def extract_panel_libraries(squashfs: Path) -> None:
    """Extract panel framework libraries."""
    print("Extracting panel framework libraries...")
    tgz_path = squashfs / "share" / "panels" / "dvpanel-framework-linux-x86_64.tgz"
    libs_dir = PREFIX / "libs"

    if tgz_path.exists():
        with tarfile.open(tgz_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name in ("libDaVinciPanelAPI.so", "libFairlightPanelAPI.so"):
                    member.name = os.path.basename(member.name)
                    tar.extract(member, libs_dir)
                    print(f"  Extracted: {member.name}")


def setup_blackmagic_raw_api() -> None:
    """Create symlinks for BlackmagicRawAPI to prevent errors."""
    print("Setting up BlackmagicRawAPI symlinks...")
    bin_dir = PREFIX / "bin"
    raw_api_dir = bin_dir / "BlackmagicRawAPI"
    raw_api_dir.mkdir(parents=True, exist_ok=True)

    lib_source = Path("../libs/libBlackmagicRawAPI.so")
    lib_source_nested = Path("../../libs/libBlackmagicRawAPI.so")

    symlink1 = bin_dir / "libBlackmagicRawAPI.so"
    symlink2 = raw_api_dir / "libBlackmagicRawAPI.so"

    if not symlink1.exists():
        symlink1.symlink_to(lib_source)
    if not symlink2.exists():
        symlink2.symlink_to(lib_source_nested)


def install_desktop_file(template_name: str, output_name: str) -> None:
    """Copy a desktop entry file to the applications directory."""
    src = DESKTOP_DIR / template_name
    dst = PREFIX / "share" / "applications" / output_name
    shutil.copy2(src, dst)
    print(f"  Installed: {output_name}")


def install_raw_player(config: BuildConfig, squashfs: Path) -> None:
    """Install Blackmagic RAW Player if present."""
    raw_player_src = squashfs / "BlackmagicRAWPlayer"
    if not raw_player_src.exists():
        return

    print("Installing Blackmagic RAW Player...")
    copy_tree(raw_player_src, PREFIX / "BlackmagicRAWPlayer")

    install_desktop_file(
        config.get_desktop_template("RAWPlayer"),
        f"{config.app_id}.RAWPlayer.desktop",
    )

    icon_src = squashfs / "graphics" / "blackmagicraw-player_256x256_apps.png"
    icon_dst = (
        PREFIX
        / "share"
        / "icons"
        / "hicolor"
        / "256x256"
        / "apps"
        / f"{config.app_id}.RAWPlayer.png"
    )
    copy_file(icon_src, icon_dst)


def install_raw_speed_test(config: BuildConfig, squashfs: Path) -> None:
    """Install Blackmagic RAW Speed Test if present."""
    speed_test_src = squashfs / "BlackmagicRAWSpeedTest"
    if not speed_test_src.exists():
        return

    print("Installing Blackmagic RAW Speed Test...")
    copy_tree(speed_test_src, PREFIX / "BlackmagicRAWSpeedTest")

    install_desktop_file(
        config.get_desktop_template("RAWSpeedTest"),
        f"{config.app_id}.RAWSpeedTest.desktop",
    )

    icon_src = squashfs / "graphics" / "blackmagicraw-speedtest_256x256_apps.png"
    icon_dst = (
        PREFIX
        / "share"
        / "icons"
        / "hicolor"
        / "256x256"
        / "apps"
        / f"{config.app_id}.RAWSpeedTest.png"
    )
    copy_file(icon_src, icon_dst)


def install_main_desktop_entry(config: BuildConfig, squashfs: Path) -> None:
    """Create main desktop entry for DaVinci Resolve."""
    print("Creating desktop entry...")

    install_desktop_file(
        config.desktop_template,
        f"{config.app_id}.desktop",
    )

    icon_src = squashfs / "graphics" / "DV_Resolve.png"
    icon_dst = (
        PREFIX
        / "share"
        / "icons"
        / "hicolor"
        / "128x128"
        / "apps"
        / f"{config.app_id}.png"
    )
    copy_file(icon_src, icon_dst)


def install_panel_setup(config: BuildConfig, squashfs: Path) -> None:
    """Install DaVinci Control Panels Setup if present."""
    panel_setup = (
        PREFIX / "DaVinci Control Panels Setup" / "DaVinci Control Panels Setup"
    )
    if not panel_setup.exists():
        return

    print("Creating DaVinci Control Panels Setup desktop entry...")

    install_desktop_file(
        config.get_desktop_template("PanelSetup"),
        f"{config.app_id}.PanelSetup.desktop",
    )

    icon_src = squashfs / "graphics" / "DV_Panels.png"
    icon_dst = (
        PREFIX
        / "share"
        / "icons"
        / "hicolor"
        / "128x128"
        / "apps"
        / f"{config.app_id}.PanelSetup.png"
    )
    copy_file(icon_src, icon_dst)


def install_remote_monitoring(config: BuildConfig, squashfs: Path) -> None:
    """Install DaVinci Remote Monitoring if present."""
    remote_monitoring = PREFIX / "bin" / "DaVinci Remote Monitoring"
    if not remote_monitoring.exists():
        return

    print("Creating DaVinci Remote Monitoring desktop entry...")

    install_desktop_file(
        config.get_desktop_template("RemoteMonitoring"),
        f"{config.app_id}.RemoteMonitoring.desktop",
    )

    icon_src = squashfs / "graphics" / "Remote_Monitoring.png"
    icon_dst = (
        PREFIX
        / "share"
        / "icons"
        / "hicolor"
        / "128x128"
        / "apps"
        / f"{config.app_id}.RemoteMonitoring.png"
    )
    copy_file(icon_src, icon_dst)


def setup_resolve(config: BuildConfig) -> None:
    """Main setup function for DaVinci Resolve."""
    print("=" * 46)
    print(f"Building {config.app_id}")
    print("=" * 46)

    # Find the installer
    installers = glob.glob("./DaVinci_Resolve_*_Linux.run")
    if not installers:
        print("Error: No DaVinci Resolve installer found!", file=sys.stderr)
        sys.exit(1)

    installer = installers[0]
    print(f"Found installer: {installer}")

    # Make the installer executable
    print("Making installer executable...")
    os.chmod(installer, 0o755)

    # Extract the Resolve installer (it's an AppImage)
    print("Extracting Resolve installer...")
    run_command([installer, "--appimage-extract"])

    squashfs = Path("squashfs-root")

    # Fix permissions on extracted files
    fix_permissions(squashfs)

    # Create required directory structure
    create_directory_structure()

    # Copy core binaries and resources
    print("Copying core files...")
    core_dirs = [
        "bin",
        "Control",
        "Certificates",
        "DaVinci Control Panels Setup",
        "Developer",
        "docs",
        "Fairlight Studio Utility",
        "Fusion",
        "graphics",
    ]
    for dir_name in core_dirs:
        src = squashfs / dir_name
        if src.exists():
            copy_tree(src, PREFIX / dir_name)
            print(f"  Copied: {dir_name}")

    # Remove conflicting libraries and copy libs
    libs_src = squashfs / "libs"
    remove_conflicting_libraries(libs_src)
    copy_tree(libs_src, PREFIX / "libs")
    print("  Copied: libs")

    # Copy remaining resources
    print("Copying additional resources...")
    additional_dirs = [
        "LUT",
        "Onboarding",
        "plugins",
        "Technical Documentation",
        "UI_Resource",
    ]
    for dir_name in additional_dirs:
        src = squashfs / dir_name
        if src.exists():
            copy_tree(src, PREFIX / dir_name)
            print(f"  Copied: {dir_name}")

    # Copy scripts
    print("Copying scripts...")
    scripts_to_copy = ["script.checkfirmware", "script.getlogs.v4", "script.start"]
    for script in scripts_to_copy:
        src = squashfs / "scripts" / script
        if src.exists():
            copy_file(src, PREFIX / "scripts" / script)
            print(f"  Copied: {script}")

    # Copy configuration files
    print("Copying configuration files...")
    config_files = ["default-config.dat", "default_cm_config.bin", "log-conf.xml"]
    for cfg in config_files:
        src = squashfs / "share" / cfg
        if src.exists():
            copy_file(src, PREFIX / "share" / cfg)
            print(f"  Copied: {cfg}")

    # Optional remote monitoring config
    remote_config = squashfs / "share" / "remote-monitoring-log-conf.xml"
    if remote_config.exists():
        copy_file(remote_config, PREFIX / "share" / "remote-monitoring-log-conf.xml")
        print("  Copied: remote-monitoring-log-conf.xml")

    # Extract panel framework libraries
    extract_panel_libraries(squashfs)

    # Setup BlackmagicRawAPI symlinks
    setup_blackmagic_raw_api()

    # Install optional components
    install_raw_player(config, squashfs)
    install_raw_speed_test(config, squashfs)
    install_main_desktop_entry(config, squashfs)
    install_panel_setup(config, squashfs)
    install_remote_monitoring(config, squashfs)

    # Cleanup
    print("Cleaning up extracted files...")
    shutil.rmtree(squashfs)

    print("=" * 46)
    print(f"Setup complete for {config.app_id}")
    print("=" * 46)
