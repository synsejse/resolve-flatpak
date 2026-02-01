"""
Allow running the package as a module: python -m resolve_builder
"""

import sys

from resolve_builder.main import main

if __name__ == "__main__":
    sys.exit(main())
