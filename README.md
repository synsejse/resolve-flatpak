# resolve-flatpak — Quickstart

Package DaVinci Resolve (free) as a Flatpak for immutable or standard Linux systems.

## Prerequisites
- Installed: `flatpak`, `flatpak-builder`
- Flathub configured: `flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo`

## Quickstart
1. Clone the repo:
   - `git clone https://github.com/synsejse/resolve-flatpak.git --recursive`
   - `cd resolve-flatpak`

2. Build (stable):
   - `flatpak-builder --install-deps-from=flathub --force-clean --repo=.repo .build-dir com.blackmagic.Resolve.yaml`

   Or build (beta):
   - `flatpak-builder --install-deps-from=flathub --force-clean --repo=.repo .build-dir com.blackmagic.Resolve.Beta.yaml`

   Note: The Beta manifest is only useful when Blackmagic publishes a beta release. If no official beta exists, the Beta build will fall back to the latest stable release.

3. Install from the local repo:
   - `flatpak --user remote-add --no-gpg-verify resolve-repo .repo`
   - `flatpak --user install resolve-repo com.blackmagic.Resolve` (or `com.blackmagic.Resolve.Beta`)

4. Run:
   - `flatpak run com.blackmagic.Resolve` (or `com.blackmagic.Resolve.Beta`)

Optional: create a bundle:
- `flatpak build-bundle .repo resolve.flatpak com.blackmagic.Resolve --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo`

## Troubleshooting (common)
- AppImage Launcher conflict: stop `appimagelauncherd` during build (it interferes with `.run` repackaging).
- GPU/drivers: Resolve requires a supported GPU and proper drivers (NVIDIA users often need proprietary drivers).
- Filesystem access: grant permissions if Resolve can't see your media:
  - `flatpak override --user --filesystem=/path/to/media com.blackmagic.Resolve`
- If builds fail, re-run the build command with `--force-clean` and check `flatpak-builder` output for the offending module.

## Project notes
- Main manifests: `com.blackmagic.Resolve.yaml` and `com.blackmagic.Resolve.Beta.yaml` (Beta falls back to stable if no official beta is available)
- Helpers and packaging code live under `python/` and `shared-modules/` (submodule).

## License & Contribution
- This project: see `LICENSE`.
- DaVinci Resolve is proprietary (see Blackmagic Design license).
- Issues and PRs welcome.
