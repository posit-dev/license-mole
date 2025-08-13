# vim: ts=3 sts=3 sw=3 expandtab:
"""Access to predefined license text.

Copyright (c) 2025 Posit Software, PBC
"""

import sys
from importlib import resources
from typing import Optional

WELL_KNOWN = [
   'SQLITE-BLESSING',
   'GPL-3.0',
   'GPL-2.0',
   'LGPL-3.0',
   'LGPL-2.1',
   'AGPL-3.0',
]

_ANCHOR = sys.modules[__name__]


def get_standard_license_text(spdx: str) -> str:
   """Retrieve the standard text for a license.

   This function should be used with caution. By necessity, this function can
   only return license text without any attribution, but most packages that use
   ISC, BSD, or MIT will include copyright attribution in their license files.

   :param spdx: The SPDX identifier of the license, or a reference returned by
      py:func:`get_standard_license_reference`.
   :return: The text of the license.
   """
   spdx = spdx.replace('spdx://', '')
   return resources.read_text(_ANCHOR, f'{spdx}.txt')


def is_safe_license_text(spdx: str, attribution: Optional[list[str]]) -> bool:
   """Identify if it is safe to use standard text for a license.

   Standard text is considered "safe" if the text exists as a resource in this
   module and one of the following is true:

   * The license is associated with a specific, known project.

   * The license text does not permit modification, so all projects using it
      will have the same text.

   * Copyright attribution has already been found from another source.

   :param spdx: The SPDX identifier of the license.
   :param attribution: A list of copyright attribution lines.
   :return: True if the standard text can be used
   """
   if not resources.is_resource(_ANCHOR, f'{spdx}.txt'):
      return False
   if attribution:
      return True
   return spdx in WELL_KNOWN


def get_standard_license_reference(spdx: str) -> str:
   """Produce a URI for the standard text for a license.

   :param spdx: The SPDX identifier of the license.
   :raises FileNotFoundError: if the license does not have standard text.
   :return: A URI for the license.
   """
   fn = f'{spdx}.txt'
   if not resources.is_resource(_ANCHOR, fn):
      raise FileNotFoundError(fn)
   return f'spdx://{spdx}'
