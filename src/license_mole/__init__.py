# vim: ts=3 sts=3 sw=3 expandtab:
"""license-mole - Functions for detecting and identifying open-source licenses.

Copyright (c) 2025 Posit Software, PBC

This __init__ module sets up package-level globals.
"""
import logging

__version__ = '0.2.1'

logger = logging.getLogger(__name__)

# Never try to fetch pages from these domain names
# because of anti-automation protections
DOMAIN_BLACKLIST = [
   'gitlab.gnome.org',
   'git.kernel.org',
]
