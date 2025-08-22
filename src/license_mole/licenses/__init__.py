# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for locating license files.

Copyright (c) 2025 Posit Software, PBC

By convention, the name ``ltype`` is used to refer to an SPDX-style license
identifier across the codebase.
"""

import glob
import os
from typing import Optional

from ..cache import download_file_cached
from ..errors import LicenseConflictError
from ..repo import find_file_in_repo
from . import resources
from .parse import LicenseInfo, normalize_license_code

# Paths to check when searching a GitHub repo for license files
GITHUB_LICENSE_PATHS = [
   '/LICENSE',
   '/LICENSE.md',
   '/LICENSE.txt',
   '/COPYING',
   '/COPYING.md',
   '/COPYRIGHT',
]

# Appended to cgit (e.g. Savannah) URLs to look for license files
# Savannah is VERY SLOW so this should be as conservative as possible
CGIT_LICENSE_PATHS = [
   '/COPYING',
   '/LICENSE',
]


def find_license_files(path: str) -> list[str]:
   """Look for license files in a directory.

   A file is considered a license file if it contains (case-insensitive)
   any of the words "LICENSE", "LICENCE", or "COPYING", or if the filename
   is (case-insensitive) "COPYRIGHT", optionally with a file extension.

   License files should only contain license information. Readme files and
   source code files are not license information and should not be returned.

   :param path: Directory to search
   :return: List of detected license files
   """
   result = []
   for fn in glob.glob(os.path.join(path, '*')):
      if fn.endswith('.js'):
         continue
      testfn = os.path.basename(fn).upper()
      if any((word in testfn) for word in ['LICENSE', 'LICENCE', 'COPYING']):
         result.append(fn)
      elif testfn.split('.')[0] == 'COPYRIGHT':
         result.append(fn)
   return [fn for fn in result if os.path.exists(fn)]


def scan_repo_for_license(repo_url: str) -> str:
   """Check a source code repository for a license file.

   The license file is downloaded if it is found, so a subsequent call to
   `download_file_cached` is guaranteed to find it in the cache.

   :param repo_url: URL to the source code repository
   :return: The URL to the license file
   """
   if repo_url.endswith('/'):
      repo_url = repo_url[:-1]
   if repo_url.startswith('https://github.com'):
      for path in GITHUB_LICENSE_PATHS:
         url = find_file_in_repo(repo_url, path)
         if url:
            return url
   elif repo_url.startswith('https://'):
      for url in CGIT_LICENSE_PATHS:
         path = f'{repo_url.strip("/")}{url}'
         if download_file_cached(path):
            return path
   return ''


def normalize_ltype_for_comparison(ltype: str) -> str:
   """Normalize an ltype into a form suitable for comparison.

   We preserve the format that the package author chose to use for rendering,
   but for comparisons we convert license identifiers into a normalized form.

   :param ltype: License identifier to normalize
   :return: Normalized license identifier
   """
   if not ltype:
      return ''
   ltype = normalize_license_code(ltype)[0].upper().replace(' ', '-')
   if ltype in {'MIT/X11', 'EXPAT'}:
      # These three licenses are different names for the same thing
      # but let's not change how the author chose to label it externally
      ltype = 'MIT'
   # This is handled inconsistently. The plural form is official.
   if ltype.endswith('LLVM-EXCEPTION'):
      ltype += 'S'
   # For the purposes of identifying a license file, treat variations such as
   # "only" or "or later version" as the same license.
   return ltype.replace('-OR-LATER', '').replace('-ONLY', '').replace('+', '')


class LicenseRegistry:
   """Singleton registry for identified license files.

   This class is used for heuristically comparing license texts to each other
   to determine if they refer to the same license, and for providing a path
   to a license file if only a license identifier is known.
   """

   def __init__(self):
      # ltype: license type code (e.g. 'MIT', 'BSD 2-Clause')
      # cs: SHA-256 checksum of normalized license text
      # source: (package key, file path)
      self._ltype_by_cs = {}
      self._cs_by_ltype = {}
      self._source_by_cs = {}
      self._clean_file_for_ltype = {}
      self._files_by_ltype = {}

   def add(self, ltype: str, license_info: LicenseInfo, source_pkg: str):
      """Add a license to the registry.

      :param ltype: License identifier
      :param license_info: Output of `analyze_license_file`
      :param source_pkg: Package identifier containing license file
      :raises LicenseConflictError: if the license file is already known under a
         different license identifier.
      """
      ltype = normalize_ltype_for_comparison(ltype)
      checksum = license_info['checksum']
      path = license_info['path']
      source = (source_pkg, path)

      existing = self._ltype_by_cs.get(checksum)
      if existing and existing != ltype:
         conflict_source = self._source_by_cs[checksum]
         raise LicenseConflictError(existing, conflict_source, ltype, source)

      self._ltype_by_cs[checksum] = ltype
      if ltype not in self._cs_by_ltype:
         self._cs_by_ltype[ltype] = set()
      self._cs_by_ltype[ltype].add(checksum)
      if checksum not in self._source_by_cs:
         self._source_by_cs[checksum] = source

      if ltype not in self._files_by_ltype:
         self._files_by_ltype[ltype] = set()
      self._files_by_ltype[ltype].add(path)
      if ltype not in self._clean_file_for_ltype and license_info['clean']:
         self._clean_file_for_ltype[ltype] = path

   def get_type_by_checksum(self, cs: str) -> Optional[str]:
      """Return the license identifier registered for a license file.

      :param cs: The checksum of the normalized license file contents
      :return: The license identifier, if known
      """
      return self._ltype_by_cs.get(cs)

   def get_file_for_type(self, ltype: str, attribution: Optional[list[str]] = None) -> Optional[str]:
      """Return the path to a copy of the text for a license.

      Only "clean" license files are candidates for this search. A "clean"
      license file does not contain any copyright information specific to any
      author or package. This is intended to be suitable to be applied to any
      package with the same license.

      :param ltype: License identifier
      :param attribution: Copyright attribution, if known
      :return: Path to the license file, if known
      """
      ltype = normalize_ltype_for_comparison(ltype)
      path = self._clean_file_for_ltype.get(ltype)
      if not path and resources.is_safe_license_text(ltype, attribution):
         path = resources.get_standard_license_reference(ltype)
      return path

   def get_source_for_checksum(self, cs: str) -> Optional[tuple[str, str]]:
      """Return a source tuple identifying where a license file was first seen.

      :param cs: The checksum of the normalized license file contents
      :return: Package and file containing license, if known
      """
      return self._source_by_cs.get(cs)


licenses = LicenseRegistry()
