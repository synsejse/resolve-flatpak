"""
Shared constants and configuration for DaVinci Resolve Flatpak build scripts.
"""

from dataclasses import dataclass

# Application identifiers
APP_ID_STABLE = "com.blackmagic.Resolve"
APP_ID_BETA = "com.blackmagic.Resolve.Beta"
APP_NAME = "DaVinci Resolve"
APP_TAG = "davinci-resolve"

# Blackmagic Design API configuration
BASE_URL = "https://www.blackmagicdesign.com/api"
DOWNLOADS_API_URL = f"{BASE_URL}/support/en/downloads.json"
DEFAULT_REFER_ID = "77ef91f67a9e411bbbe299e595b4cfcc"

# HTTP request configuration
COOKIES: dict[str, str] = {
    "_ga": "GA1.2.1849503966.1518103294",
    "_gid": "GA1.2.953840595.1518103294",
}

HEADERS: dict[str, str] = {
    "Host": "www.blackmagicdesign.com",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.blackmagicdesign.com",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/77.0.3865.75 "
        "Safari/537.36"
    ),
    "Content-Type": "application/json;charset=UTF-8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Authority": "www.blackmagicdesign.com",
    "Cookie": "_ga=GA1.2.1849503966.1518103294; _gid=GA1.2.953840595.1518103294",
}

# Download chunk size (1 MB)
DOWNLOAD_CHUNK_SIZE = 1024 * 1024


@dataclass
class BuildConfig:
    """Configuration for the build process."""

    is_beta: bool = False

    @property
    def app_id(self) -> str:
        """Get the application ID based on build type."""
        return APP_ID_BETA if self.is_beta else APP_ID_STABLE

    @property
    def app_name(self) -> str:
        """Get the display name for the application."""
        return f"{APP_NAME} (Beta)" if self.is_beta else APP_NAME

    @property
    def template_prefix(self) -> str:
        """Get the template filename prefix based on build type."""
        return APP_ID_BETA if self.is_beta else APP_ID_STABLE

    @property
    def metainfo_template(self) -> str:
        """Get the metainfo template filename."""
        return f"{self.template_prefix}.metainfo.xml"

    @property
    def desktop_template(self) -> str:
        """Get the main desktop entry template filename."""
        return f"{self.template_prefix}.desktop"

    def get_desktop_template(self, suffix: str) -> str:
        """Get a desktop entry template filename with a suffix (e.g., 'RAWPlayer')."""
        return f"{self.template_prefix}.{suffix}.desktop"
