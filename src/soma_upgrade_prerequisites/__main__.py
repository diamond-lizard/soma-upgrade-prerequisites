#!/usr/bin/env python3
"""Entry point for python -m soma_upgrade_prerequisites."""
# Entry point for python -m soma_upgrade_prerequisites.
from .main import cli

try:
    cli()
except KeyboardInterrupt:
    raise SystemExit(1) from None
