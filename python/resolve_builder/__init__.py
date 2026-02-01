"""
Resolve Builder - Build tools for packaging DaVinci Resolve as a Flatpak.
"""

__version__ = "1.0.0"

from resolve_builder.constants import (
    APP_ID_BETA,
    APP_ID_STABLE,
    APP_NAME,
    APP_TAG,
    BASE_URL,
    DEFAULT_REFER_ID,
    DOWNLOADS_API_URL,
    BuildConfig,
)
from resolve_builder.download import download_using_id, get_latest_version_information
from resolve_builder.main import main
from resolve_builder.metainfo import build_metainfo
from resolve_builder.setup import setup_directories, setup_resolve
from resolve_builder.version import Version

__all__ = [
    "__version__",
    # Constants
    "APP_ID_BETA",
    "APP_ID_STABLE",
    "APP_NAME",
    "APP_TAG",
    "BASE_URL",
    "DEFAULT_REFER_ID",
    "DOWNLOADS_API_URL",
    # Classes
    "BuildConfig",
    "Version",
    # Functions
    "build_metainfo",
    "download_using_id",
    "get_latest_version_information",
    "main",
    "setup_directories",
    "setup_resolve",
]
