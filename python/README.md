# Resolve Builder

Build tools for packaging DaVinci Resolve as a Flatpak.

## Installation

### For Development

```bash
cd python
pip install -e ".[dev]"
```

### For Production

```bash
cd python
pip install .
```

## Usage

### As a Command-Line Tool

After installation, you can run the builder directly:

```bash
resolve-builder
```

To build the beta version:

```bash
resolve-builder --beta
```

### As a Python Module

```bash
python -m resolve_builder
```

### Programmatic Usage

```python
from resolve_builder import (
    get_latest_version_information,
    download_using_id,
    setup_directories,
    setup_resolve,
    build_metainfo,
)

# Get latest version info
version, release_id, download_id = get_latest_version_information(
    app_tag="davinci-resolve",
    stable=True,
)
print(f"Latest version: {version}")

# Download the installer
download_using_id(download_id)

# Set up the flatpak
setup_directories()
setup_resolve()
build_metainfo()
```

## Package Structure

```
resolve_builder/
├── __init__.py      # Package exports
├── __main__.py      # Entry point for `python -m resolve_builder`
├── constants.py     # Shared constants and configuration
├── download.py      # Download utilities for Blackmagic API
├── main.py          # Main build orchestration
├── metainfo.py      # AppStream metainfo generation
├── setup.py         # Flatpak setup and file installation
└── version.py       # Version class for version management
```

## Development

### Running Linters

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run ruff linter
ruff check .

# Run ruff formatter
ruff format .

# Run type checker
mypy resolve_builder
```

### Running Tests

```bash
# TODO: Add tests
```

## License

See the [LICENSE](../LICENSE) file in the root directory.