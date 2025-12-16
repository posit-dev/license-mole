# vim: ts=3 sts=3 sw=3 expandtab:
"""Base class for package descriptions.

Copyright (c) 2025 Posit Software, PBC
SPDX-License-Identifier: MIT
"""

from typing import Any, ItemsView, Optional, Self, cast

from ..config import get_overrides
from ..licenses import find_license_files, licenses
from ..licenses.collection import LicenseCollection
from ..pathselector import PathSelector

VersionKey = tuple[int, ...]


def version_tuple(version: Optional[str]) -> VersionKey:
   """Split a version into a tuple suitable for sorting.

   :param version: The package's version string
   :return: A tuple of version components
   """
   if not version:
      return ()
   parts: list[int] = []
   for part in version.replace('-', '.').lower().split('.'):
      try:
         parts.append(int(part.replace('v', '')))
      except ValueError:
         has_ival = False
         ival = 0
         cval = 0
         for ch in part:
            if ch >= '0' and ch <= '9':
               if cval:
                  parts.append(-cval)
                  cval = 0
               ival = ival * 10 + int(ch)
               has_ival = True
            else:
               if has_ival:
                  parts.append(ival)
                  has_ival = False
                  ival = 0
               cval = cval * 256 + ord(ch)
         if has_ival:
            parts.append(ival)
         elif cval:
            parts.append(-cval)
   return tuple(parts)


def _optional_extend(info: dict[str, Any], key: str) -> dict[str, Any]:
   """Return a modifier dict to extend another dict.

   If the provided key exists in `info` and the value is truthy, then the
   returned modifier dict contains that key and value. Otherwise, the
   returned dict is empty.

   :param info: Source dictionary
   :param key: Key to check
   :return: Modifier dictionary
   """
   value = info.get(key)
   if value:
      return {key: value}
   return {}


class BasePackage:
   """Base class for package descriptions.

   The constructor scans the package directory for license files.

   Subclasses should be careful to honor values found in py:attr:`self._overrides`.

   :param name: The display name of the package
   :param path: The path containing the package's files
   :param version: The version of the package, if known
   :param author: The author of the package, if known
   :param scan: If False, disables automatic scanning for license files
   """

   package_type: str
   """Label for rendering what kind of package this is."""
   name: str
   """Human-readable name of the package."""
   path: PathSelector
   """Path to the root of the package."""
   version: Optional[str]
   """The version of the package."""
   licenses: LicenseCollection
   """Information about detected licenses."""
   ignored: bool
   """If True, completely ignore this package.

   Scanners may choose to look for transitive dependencies in ignored packages.
   """

   def __init__(self, name: str, path: PathSelector, version: str = '', author: str = '', scan: bool = True):
      self._populate(name, path, version, author)
      self.ignored = self._overrides.get('ignored') or False

      files = self._overrides.get('license_files')
      if scan and files is None and self.path:
         files = [path.to_selector(p) for p in find_license_files(self.path.to_absolute())]
      for fn in files or []:
         if fn.repo == '@':
            abspath = path.to_absolute(fn.path)
         else:
            abspath = fn.to_absolute()
         info = self.licenses.add_file(abspath)
         if info['spdx']:
            if len(info['spdx']) == 1:
               # Only register the file if it's unambiguous
               licenses.add(info['spdx'][0], info, self.name)
            for ltype in info['spdx']:
               self.licenses.link_file(ltype, info['path'])

   def _prepopulate(self, data: dict[str, Any]):
      """Prepare a bare object to be populated.

      The default implementation does nothing. Subclasses may reimplement
      this method to make changes to the object during deserialization before
      the call to _populate.

      :param data: Serialized data from the cache
      """

   def _populate(self, name: str, path: PathSelector, version: str, author: str):
      """Populate a bare object with basic properties.

      :param name: The display name of the package
      :param path: The path containing the package's files
      :param version: The version of the package, if known
      :param author: The author of the package, if known
      """
      self._original_name = name
      self.name = name
      self.path = path
      self.version = version
      self._overrides = get_overrides(self.key)
      self.permit_license_change = self._overrides.get('permit_license_change', False)

      self._rename = self._overrides.get('rename', '')
      if self._rename:
         self.name = self._rename
         # force the key property to be recomputed with the modified value
         del self.key

      author = self._overrides.get('author', author)
      self.licenses = LicenseCollection(package=self.key, base_path=path.to_absolute(), author=author)
      for ltype in self._overrides.get('license', ()):
         self.licenses.add(ltype)

      if 'attribution' in self._overrides:
         self.licenses.attribution = self._overrides['attribution']

   @classmethod
   def deserialize(cls, data: dict[str, Any], selector: PathSelector) -> Self:
      """Construct a package from serialized data.

      :param data: Serialized data
      :param selector: The selector that paths are relative to
      :return: A new package instance
      """
      pkg = cls.__new__(cls)
      pkg._deserialize(data, selector)
      return pkg

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      """Fill a package from serialized data.

      This should only be called by `deserialize`.

      :param data: Serialized data
      :param selector: The selector that paths are relative to
      """
      self._prepopulate(data)
      self._populate(
         data['name'],
         selector.to_selector(data['path']),
         data['version'],
         data.get('author', ''),
      )
      self.ignored = False
      if data.get('attribution'):
         self.licenses.attribution = data['attribution']

      for ltype in data.get('licenses', []):
         self.licenses.add(ltype)

      repo = selector.to_selector('')
      for fn, info in data.get('license_files', {}).items():
         self.licenses.add_file_from_cache(repo.to_absolute(fn), info)

   @property
   def version_tuple(self) -> VersionKey:
      """A tuple suitable for comparing package versions."""
      return version_tuple(self.version)

   @property
   def key(self) -> str:
      """A unique key identifying the package.

      Subclasses must implement this property.

      Keys should be of the form `type::name[@version]`.
      """
      raise NotImplementedError()

   @property
   def url(self) -> str:
      """The URL to a "homepage" for the package.

      Ideally this should be a link to the source code repository, but
      a link to a package page is acceptable.

      Subclasses must implement this property.
      """
      raise NotImplementedError()

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      Subclasses should override this to add additional fields.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      lfiles = {}
      has_attrib = False
      for fn, info in cast('ItemsView[str, dict[str, Any]]', self.licenses.files.items()):
         rel = selector.to_relative(fn)
         if info['attribution']:
            has_attrib = True
         lfiles[rel] = {
            'checksum': info['checksum'],
            **_optional_extend(info, 'attribution'),
            **_optional_extend(info, 'spdx'),
            **_optional_extend(info, 'guess'),
            **_optional_extend(info, 'multi'),
            **_optional_extend(info, 'clean'),
         }

      data: dict[str, Any] = {
         'name': self._original_name,
         'path': selector.to_relative(self.path.to_absolute()),
         'version': self.version,
      }

      if self.licenses.author:
         data['author'] = self.licenses.author
      if attrib := has_attrib and self.licenses.get_attribution_from_files():
         data['attribution'] = attrib
      if self.licenses:
         data['licenses'] = sorted(self.licenses)
      if lfiles:
         data['license_files'] = lfiles
      return data
