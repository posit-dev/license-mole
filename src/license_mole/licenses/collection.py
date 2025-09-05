# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for managing a collection of licenses for a package.

Copyright (c) 2025 Posit Software, PBC
"""

from functools import cached_property
from typing import Any, Iterator, Optional, Union, cast

from ..errors import LicenseConflictError
from . import licenses, normalize_ltype_for_comparison
from .parse import LicenseInfo, analyze_license_file, get_readme_attribution, normalize_license_code

LABEL_BLACKLIST = ['BSD', 'DUAL-LICENSE']


def normalize_license_url(url: str) -> str:
   """Clean up a URL pointing to a license file.

   The returned URL should be plain text (not HTML) and ideally retrieved
   over HTTPS instead of HTTP. The URL is not guaranteed to exist.

   If the provided path is not a URL, it is returned unchanged.

   :param url: The URL to clean
   :return: The cleaned URL
   """
   url = url.replace('http://github.com/', 'https://github.com/')
   if '/blob/' in url:
      url = url.replace('/blob/', '/raw/')
   return url


class LicenseCollection:
   """A collection of licenses for a package.

   :param package: The package identifier (see BasePackage.key)
   :param base_path: The directory containing the package
   :param author: The author of the package, if known
   """

   links: dict[str, str]
   """Mapping from normalized license identifier to file paths"""
   files: dict[str, LicenseInfo]
   """Mapping from file paths to license descriptions.

   See :py:func:`analyze_license_file` for details.
   """

   def __init__(self, package: str, base_path: str, author: Optional[str] = None):
      self.package = package
      self.base_path = base_path
      self._ltypes: set[str] = set()
      self._normalized: set[str] = set()
      self.links = {}
      self.author = author
      self.files = {}
      self._unlinked_ltypes: set[str] = set()
      self._unlinked_files: set[str] = set()

   @cached_property
   def attribution(self) -> list[str]:
      """A list of copyright attribution lines.

      Typically these lines are in the form "Copyright (c) <year> <author>".
      """
      attr = self.get_attribution_from_files()
      if not attr and self.base_path:
         attr += get_readme_attribution(self.base_path)
      if not attr and self.author:
         attr.append(f'Published by {self.author}')
      return attr

   def get_attribution_from_files(self) -> list[str]:
      """Collect attribution lines from associated files.

      Unlike the `attribution` property, this is not cached.

      :return: A list of copyright atribution lines.
      """
      attr = []
      for info in self.files.values():
         attr += info['attribution']
      return attr

   @property
   def unlinked_ltypes(self) -> list[str]:
      """A list of license identifiers that have not been matched with a file."""
      return list(self._unlinked_ltypes)

   @property
   def unlinked_files(self) -> dict[str, LicenseInfo]:
      """A list of files that have not been matched with a license identifier."""
      result = {}
      for fn in self._unlinked_files:
         result[fn] = self.files[fn]
      return result

   def is_empty(self) -> bool:
      """Return True if the collection contains no license information."""
      return (len(self._ltypes) + len(self.files)) == 0

   def count_unlinked(self) -> tuple[int, int]:
      """Return the number of unlinked license identifiers and unlinked files."""
      return (len(self._unlinked_ltypes), len(self._unlinked_files))

   def has(self, ltype: str) -> bool:
      """Check to see if the collection contains the requested license.

      :param ltype: The license identifier
      :return: Whether the collection contains the license
      """
      return normalize_ltype_for_comparison(ltype) in self._normalized

   def add(self, ltype_or_ltypes: Union[str, tuple[str, ...]]):
      """Add a license identifier to the collection.

      :param ltype_or_ltypes: License identifier(s) to add
      :raises ValueError: if a license identifier is invalid
      """
      if isinstance(ltype_or_ltypes, str):
         raw_ltypes = cast('tuple[str, ...]', (ltype_or_ltypes,))
      else:
         raw_ltypes = ltype_or_ltypes
      for ltypes in raw_ltypes:
         for ltype in normalize_license_code(ltypes):
            if not ltype:
               raise ValueError('Blank license type')
            normalized = normalize_ltype_for_comparison(ltype)
            if normalized in LABEL_BLACKLIST:
               # Labels in the blacklist are ambiguous about which license they
               # represent. Skipping it here will either detect it from the
               # license file or force the user to provide an override.
               continue
            self._ltypes.add(ltype)
            if not normalized:
               raise ValueError('Blank license type')
            self._normalized.add(normalized)
            if normalized not in self.links:
               self._unlinked_ltypes.add(normalized)

   def __iter__(self) -> Iterator[str]:
      """Return an iterator over the license identifiers."""
      return self._ltypes.__iter__()

   def __len__(self) -> int:
      """Return the number of license identifiers in the collection."""
      return len(self._ltypes)

   def add_file_from_cache(self, path: str, cached: dict[str, Any]):
      """Add a file to the collection based on cached data.

      :param path: Path to the license file
      :param cached: Data from the cache
      """
      info: LicenseInfo = {
         'author': self.author,
         'path': path,
         'attribution': cached.get('attribution', []),
         'spdx': tuple(cached.get('spdx', [])),
         'guess': cached.get('guess'),
         'checksum': cached['checksum'],
         'multi': bool(cached.get('multi')),
         'clean': bool(cached.get('clean')),
      }
      self.files[path] = info
      if info['spdx']:
         for ltype in info['spdx']:
            ltype = normalize_ltype_for_comparison(ltype)
            self.link_file(ltype, path)
      else:
         self._unlinked_files.add(path)

   def add_file(self, path: str) -> LicenseInfo:
      """Add a file to the collection.

      If the license contains an SPDX identifier or can be unambiguously
      identified from its filename, the file is linked to the corresponding
      license identifier.

      This function returns the result of analyzing the file.

      :param path: Path to the license file
      :return: License file description (see `analyze_license_file`)
      """
      path = normalize_license_url(path)
      info = analyze_license_file(path, self.author)
      self.files[path] = info
      linked = False
      if info['spdx']:
         for ltype in info['spdx']:
            self.add(ltype)
            ltype = normalize_ltype_for_comparison(ltype)
            self.link_file(ltype, path)
            self._unlinked_ltypes.discard(ltype)
            linked = True
      if not linked:
         self._unlinked_files.add(path)
      return info

   def get_file(self, ltype: str) -> Optional[str]:
      """Return the license file linked to an identifier.

      :param ltype: The license identifier
      :return: The path to the license file, if known
      """
      return self.links.get(normalize_ltype_for_comparison(ltype))

   def link_file(self, ltype: str, path: str) -> bool:
      """Links a license file to a license type.

      If the file was already linked to the identifier, this function does
      nothing and returns False.

      If the identifier was not linked to a file, this function returns False.

      If there was already a link to a different license file, this function
      chooses whether to keep the old link or replace it with the new link.
      In either case, this function returns True.

      :param ltype: The license identifier for the file
      :param path: The path to the license file
      :return: True if there was already a link to a different license file
      """
      self._unlinked_files.discard(path)
      ltype = normalize_ltype_for_comparison(ltype)
      info = self.files[path]
      if not info['multi']:
         licenses.add(ltype, info, self.package)
      if ltype not in self.links:
         self.links[ltype] = path
         self._unlinked_ltypes.discard(ltype)
         return False

      old = self.links[ltype]
      if old == path:
         return False

      self._unlinked_ltypes.discard(ltype)

      # prefer Markdown if all else is equal
      old_md = '.md' in old or '.markdown' in old
      new_md = '.md' in path or '.markdown' in path
      if old_md and not new_md:
         return True
      if new_md and not old_md:
         self.links[ltype] = path
         return True

      # prefer shorter filenames if all else is equal
      if len(path) < len(old):
         self.links[ltype] = path
      return True

   def auto_link_files(self) -> bool:
      """Heuristically links license files to license identifiers.

      If any files in the collection have an unambiguous SPDX identifier, they
      are linked to those identifiers in the collection.

      If the collection only contains one unlinked identifier and one unlinked
      file, they are linked and this association is added to the main license
      registry. This may raise LicenseConflictError if the content of the file
      does not match the license identifier.

      :raises LicenseConflictError: if the license file has been seen with a
         different identifier
      :return: True if all licenses in the collection have been linked
      """
      for path in self.links.values():
         # make sure any files that were linked before aren't considered unlinked
         self._unlinked_files.discard(path)

      for fn in list(self._unlinked_files):
         info = self.files[fn]
         for ltype in info['spdx']:
            if self.has(ltype):
               self.link_file(ltype, fn)

      if len(self._unlinked_ltypes) == 0 and len(self._unlinked_files) == 0:
         return not self.is_empty()

      if len(self._unlinked_ltypes) == 1 and len(self._unlinked_files) == 1:
         ltype = next(iter(self._unlinked_ltypes))
         info = self.files[self._unlinked_files.pop()]
         check: tuple[str, ...] = ()
         if info['spdx']:
            check = tuple(normalize_ltype_for_comparison(l) for l in info['spdx'])
         elif licenses.get_type_by_checksum(info['checksum']) or info['guess']:
            check = (
               normalize_ltype_for_comparison(licenses.get_type_by_checksum(info['checksum']) or info['guess'] or ''),
            )
         if check and ltype not in check:
            this_source = (self.package, info['path'])
            conflict_source = licenses.get_source_for_checksum(info['checksum']) or this_source
            raise LicenseConflictError('/'.join(check), conflict_source, ltype, this_source)
         self.links[ltype] = info['path']
         self._unlinked_ltypes.discard(ltype)
         licenses.add(ltype, info, self.package)

      return not self.is_empty() and sum(self.count_unlinked()) == 0
