"""
Build AppStream metainfo XML for DaVinci Resolve.
"""

import datetime
import re
import sys
from pathlib import Path
from string import Template
from typing import Any, cast

import requests

from resolve_builder.constants import APP_TAG, DOWNLOADS_API_URL, BuildConfig
from resolve_builder.version import Version

METAINFO_DIR = Path("metainfo")


def fetch_downloads() -> dict[str, Any]:
    """Fetch downloads information from Blackmagic API."""
    try:
        response = requests.get(DOWNLOADS_API_URL, timeout=30)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
    except requests.RequestException as e:
        print(f"Error fetching downloads: {e}", file=sys.stderr)
        raise


def parse_version_from_download(linux_download: dict[str, Any]) -> Version:
    """Parse version information from a Linux download entry."""
    beta_match = re.match(r".*Beta (\d+)", linux_download["downloadTitle"])
    beta = -1
    if beta_match and beta_match.group(1):
        beta = int(beta_match.group(1))

    return Version(
        major=linux_download["major"],
        minor=linux_download["minor"],
        patch=linux_download["releaseNum"],
        build=linux_download["releaseId"],
        beta=beta,
    )


def format_release_entry(version: Version, date: str, description: str) -> str:
    """Format a single release entry for the metainfo XML."""
    return f"""    <release version="{version}" date="{date}">
      <description>
        <p>{description}</p>
      </description>
    </release>"""


def build_metainfo(config: BuildConfig, output_path: str | Path | None = None) -> None:
    """
    Fetch version info from Blackmagic API and generate metainfo XML.

    Args:
        config: Build configuration object
        output_path: Path where the metainfo file will be written.
    """
    if output_path is None:
        output_path = Path(f"/app/share/metainfo/{config.app_id}.metainfo.xml")
    else:
        output_path = Path(output_path)

    parsed_response = fetch_downloads()

    latest_description = ""
    releases = ""

    for download in parsed_response["downloads"]:
        if "Linux" not in download["urls"]:
            continue

        linux_download = download["urls"]["Linux"][0]
        if linux_download.get("product") != APP_TAG:
            continue

        description = download["desc"]
        version = parse_version_from_download(linux_download)

        try:
            date = datetime.datetime.strptime(download["date"], "%d %b %Y").strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            print(
                f"Warning: Could not parse date '{download['date']}'", file=sys.stderr
            )
            continue

        if not latest_description:
            latest_description = description

        releases += format_release_entry(version, date, description) + "\n"

    if not releases:
        print("Warning: No releases found for DaVinci Resolve", file=sys.stderr)

    # Load template and substitute only RELEASES and DESCRIPTION
    template_path = METAINFO_DIR / config.metainfo_template
    template = Template(template_path.read_text())
    content = template.safe_substitute(
        DESCRIPTION=latest_description,
        RELEASES=releases,
    )

    output_path.write_text(content, encoding="utf-8")
    print(f"Metainfo written to {output_path}")
