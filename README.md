# resolve-flatpak

Package [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (Free Version) as a Flatpak for Linux systems.

This is particularly useful for immutable distributions like Fedora Silverblue, where traditional installation methods aren't available.

> **Note:** This project is a work-in-progress but is functional ("works-for-me™").

## Prerequisites

- [Flatpak](https://flatpak.org/setup/) installed and configured
- [flatpak-builder](https://docs.flatpak.org/en/latest/flatpak-builder.html) installed
- Flathub repository added: `flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo`

## Usage

### 1. Clone the Repository

```bash
git clone https://github.com/synsejse/resolve-flatpak.git --recursive
cd resolve-flatpak
```

### 2. Build the Flatpak

#### Stable Version

```bash
flatpak-builder --install-deps-from=flathub --force-clean --repo=.repo .build-dir com.blackmagic.Resolve.yaml
```

#### Beta Version

```bash
flatpak-builder --install-deps-from=flathub --force-clean --repo=.repo .build-dir com.blackmagic.Resolve.Beta.yaml
```

> **Note:** Stable and Beta versions have different app IDs, so they can be installed side-by-side.

### 3. Install from Local Build

```bash
flatpak --user remote-add --no-gpg-verify resolve-repo .repo

# Install stable version
flatpak --user install resolve-repo com.blackmagic.Resolve

# Or install beta version
flatpak --user install resolve-repo com.blackmagic.Resolve.Beta
```

### 4. (Optional) Create a Redistributable Bundle

```bash
# Stable
flatpak build-bundle .repo resolve.flatpak com.blackmagic.Resolve --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo

# Beta
flatpak build-bundle .repo resolve-beta.flatpak com.blackmagic.Resolve.Beta --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
```

## Running DaVinci Resolve

After installation, you can run DaVinci Resolve from your application launcher or via the command line:

```bash
# Stable version
flatpak run com.blackmagic.Resolve

# Beta version
flatpak run com.blackmagic.Resolve.Beta
```

## Troubleshooting

### AppImage Launcher Conflict

If you have `appimagelauncherd` (AppImage Launcher daemon) installed and enabled, you **must** temporarily disable it before building. It conflicts with flatpak-builder during the `.run` file repackaging process.

Disable it with:

```bash
systemctl --user stop appimagelauncherd
```

Or disable it through the AppImage Launcher GUI settings.

### GPU Issues

DaVinci Resolve requires a supported GPU. If you encounter issues:

1. Ensure you have the latest GPU drivers installed
2. For NVIDIA users, make sure the proprietary drivers are installed
3. Check that your GPU meets the [minimum requirements](https://www.blackmagicdesign.com/products/davinciresolve/techspecs)

### Permission Issues

If Resolve can't access your media files, you may need to grant additional filesystem permissions:

```bash
flatpak override --user --filesystem=/path/to/your/media com.blackmagic.Resolve
```

## Finding Download IDs

To find available download IDs for the free version (useful for debugging or manual downloads):

```bash
curl -s https://www.blackmagicdesign.com/api/support/nz/downloads.json | \
    jq -r '.downloads[]
           | select(.urls["Linux"] != null)
           | select(.urls["Linux"][0]["product"] == "davinci-resolve")
           | [.urls["Linux"][0].downloadTitle, .urls["Linux"][0].downloadId]
           | @tsv'
```

## Project Structure

```
resolve-flatpak/
├── com.blackmagic.Resolve.yaml        # Flatpak manifest (stable)
├── com.blackmagic.Resolve.Beta.yaml   # Flatpak manifest (beta)
├── python/                        # Python package
│   ├── pyproject.toml            # Package configuration
│   ├── README.md                 # Package documentation
│   └── resolve_builder/          # Main package
│       ├── __init__.py           # Package exports
│       ├── __main__.py           # Entry point for `python -m resolve_builder`
│       ├── constants.py          # Shared constants and configuration
│       ├── download.py           # Download utilities for Blackmagic API
│       ├── main.py               # Main build orchestration
│       ├── metainfo.py           # AppStream metainfo generation
│       ├── setup.py              # Flatpak setup and file installation
│       └── version.py            # Version class for version management
├── desktop/                       # Desktop entry templates
│   ├── stable/                   # Stable version templates
│   │   ├── com.blackmagic.Resolve.desktop
│   │   ├── com.blackmagic.Resolve.PanelSetup.desktop
│   │   ├── com.blackmagic.Resolve.RAWPlayer.desktop
│   │   ├── com.blackmagic.Resolve.RAWSpeedTest.desktop
│   │   └── com.blackmagic.Resolve.RemoteMonitoring.desktop
│   └── beta/                     # Beta version templates
│       ├── com.blackmagic.Resolve.Beta.desktop
│       ├── com.blackmagic.Resolve.Beta.PanelSetup.desktop
│       ├── com.blackmagic.Resolve.Beta.RAWPlayer.desktop
│       ├── com.blackmagic.Resolve.Beta.RAWSpeedTest.desktop
│       └── com.blackmagic.Resolve.Beta.RemoteMonitoring.desktop
├── metainfo/                      # AppStream metainfo templates
│   ├── stable/
│   │   └── com.blackmagic.Resolve.metainfo.xml
│   └── beta/
│       └── com.blackmagic.Resolve.Beta.metainfo.xml
├── bin/                           # Shell scripts
│   └── resolve.sh                # Launcher script
├── shared-modules/               # Git submodule for shared Flatpak modules
└── run_complete_installation.sh  # Build environment bootstrap
```

## Licensing

- **This project:** See [LICENSE](LICENSE)
- **DaVinci Resolve:** Proprietary software by Blackmagic Design. See their [license terms](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion).
- **Logo (`logo.png`):** Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), sourced from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:DaVinci_Resolve_Studio.png) and cropped.

## Related Links

- [Flathub Forum: DaVinci Resolve Feature Requests](https://discourse.flathub.org/t/davinci-resolve-flatpak-request/842)
- [Blackmagic Forum: DaVinci Resolve Flatpak Request](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=186259)
- [makeresolvedeb](https://www.danieltufvesson.com/makeresolvedeb) - Inspiration for the setup scripts

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
