"""
Version class for DaVinci Resolve version management.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Version:
    """
    Represents a DaVinci Resolve version.

    Attributes:
        major: Major version number
        minor: Minor version number
        patch: Patch version number
        beta: Beta version number (-1 for stable releases)
        build: Build identifier
    """

    major: int
    minor: int
    patch: int
    beta: int
    build: int

    def __str__(self) -> str:
        """
        Return string representation of version.

        For stable releases: "major.minor.patch"
        For beta releases: "major.minor.patch.beta+build"
        """
        if self.beta == -1:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}.{self.patch}.{self.beta}+{self.build}"

    @property
    def is_stable(self) -> bool:
        """Return True if this is a stable (non-beta) release."""
        return self.beta == -1

    @property
    def is_beta(self) -> bool:
        """Return True if this is a beta release."""
        return self.beta != -1

    def as_tuple(self) -> tuple[int, int, int, int, int]:
        """Return version components as a tuple for comparison."""
        return (self.major, self.minor, self.patch, self.beta, self.build)
