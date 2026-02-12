"""
Main entry point for building DaVinci Resolve Flatpak (Free Version).
"""

import sys
import zipfile
from pathlib import Path

from resolve_builder.constants import APP_TAG, DEFAULT_REFER_ID, BuildConfig
from resolve_builder.download import download_using_id, get_latest_version_information
from resolve_builder.metainfo import build_metainfo
from resolve_builder.setup import setup_directories, setup_resolve


def main() -> int:
    """
    Main entry point for the build process.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    is_beta = "--beta" in sys.argv
    config = BuildConfig(is_beta=is_beta)

    print(f"Building {config.app_id}")
    print(f"Using tag: {APP_TAG}")
    print(f"Mode: {'beta' if config.is_beta else 'stable'}")

    print("Requesting version information...")
    try:
        version, _release_id, download_id = get_latest_version_information(
            refer_id=DEFAULT_REFER_ID,
            app_tag=APP_TAG,
            stable=not config.is_beta,
        )
    except Exception as e:
        print(f"Error fetching version information: {e}")
        return 1

    print(f"Found version: {version}")

    resolve_zip = Path("resolve.zip")
    if not resolve_zip.is_file():
        print(f"Downloading latest version of {config.app_name}...")
        try:
            download_using_id(download_id, refer_id=DEFAULT_REFER_ID)
        except Exception as e:
            print(f"Error downloading {config.app_name}: {e}")
            return 1
        print()
    else:
        print("Using user supplied resolve.zip (testing)")

    print("Extracting resolve installation...")
    try:
        with zipfile.ZipFile(resolve_zip, "r") as zip_file:
            zip_file.extractall(".")
    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file: {e}")
        return 1
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return 1

    print("Setting up directories...")
    try:
        setup_directories()
    except Exception as e:
        print(f"Error setting up directories: {e}")
        return 1

    print("Setting up DaVinci Resolve...")
    try:
        setup_resolve(config)
    except Exception as e:
        print(f"Error setting up DaVinci Resolve: {e}")
        return 1

    print("Building metainfo...")
    try:
        build_metainfo(config)
    except Exception as e:
        print(f"Error building metainfo: {e}")
        return 1

    print(f"Done! Built {config.app_name} {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
