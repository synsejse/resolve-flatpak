"""
Download utilities for DaVinci Resolve.
"""

import json
from pathlib import Path

import requests
from tqdm import tqdm

from resolve_builder.constants import (
    BASE_URL,
    COOKIES,
    DEFAULT_REFER_ID,
    DOWNLOAD_CHUNK_SIZE,
    HEADERS,
)
from resolve_builder.version import Version


def get_latest_version_information(
    app_tag: str,
    refer_id: str = DEFAULT_REFER_ID,
    stable: bool = True,
) -> tuple[Version, str, str]:
    """
    Fetch the latest version information for DaVinci Resolve.

    Args:
        app_tag: The product tag (e.g., "davinci-resolve")
        refer_id: The referral ID for the API request
        stable: If True, fetch latest stable version; otherwise fetch latest beta

    Returns:
        Tuple of (Version, release_id, download_id)

    Raises:
        requests.HTTPError: If the API request fails
        KeyError: If the response is missing expected fields
    """
    endpoint = (
        f"{BASE_URL}/support/latest-stable-version/{app_tag}/linux"
        if stable
        else f"{BASE_URL}/support/latest-version/{app_tag}/linux"
    )

    response = requests.get(
        endpoint,
        cookies=COOKIES,
        headers={
            **HEADERS,
            "Referer": f"https://www.blackmagicdesign.com/support/download/{refer_id}/Linux",
        },
        timeout=30,
    )
    response.raise_for_status()

    parsed_response = response.json()
    linux_info = parsed_response["linux"]

    version = Version(
        major=linux_info["major"],
        minor=linux_info["minor"],
        patch=linux_info["releaseNum"],
        build=linux_info["build"],
        beta=linux_info.get("beta", -1),
    )

    return (version, linux_info["releaseId"], linux_info["downloadId"])


def download_using_id(
    download_id: str,
    refer_id: str = DEFAULT_REFER_ID,
    output_path: str | Path = "./resolve.zip",
) -> None:
    """
    Download DaVinci Resolve installer using the download ID.

    Args:
        download_id: The download ID from Blackmagic API
        refer_id: The referral ID for the API request
        output_path: Path where the downloaded file will be saved

    Raises:
        requests.HTTPError: If the download request fails
    """
    download_url_data = {
        "firstname": "Flatpak",
        "lastname": "Builder",
        "email": "someone@flathub.org",
        "phone": "202-555-0194",
        "country": "us",
        "state": "New York",
        "city": "FPK",
        "street": "Bowery 146",
        "product": "DaVinci Resolve",
    }

    # Request download URL
    download_url_response = requests.post(
        f"{BASE_URL}/register/us/download/{download_id}",
        cookies=COOKIES,
        headers={
            **HEADERS,
            "Referer": f"https://www.blackmagicdesign.com/support/download/{refer_id}/Linux",
        },
        data=json.dumps(download_url_data),
        timeout=30,
    )
    download_url_response.raise_for_status()

    download_url = download_url_response.text

    # Download the file with progress bar
    download_response = requests.get(download_url, stream=True, timeout=(30, 300))
    download_response.raise_for_status()

    total_size = int(download_response.headers.get("Content-Length", 0))

    with (
        open(output_path, "wb") as f,
        tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar,
    ):
        for chunk in download_response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
