# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for collecting manual dependency information.

Copyright (c) 2025 Posit Software, PBC

For dependencies that are not managed with a package manager, license-mole
supports a format in the style of a CMake function. A minimal dependency
definition looks like this::

   dependency(<IDENTIFIER>
      DEPNAME    "<display-name>"
      REPOSITORY "<url>"
   )

Text in a dependency file that is outside of a ``dependency()`` block is
ignored. This allows the use of a ``CMakeLists.txt`` file containing these
definitions. Comments begin with a ``#`` character.

The following arguments are supported:

* ``<IDENTIFIER>``: *Required.* A unique identifier for this dependency. This
   identifier should not be quoted and spaces are not allowed. While
   license-mole places no other restrictions on this identifier, it should be a
   valid CMake variable name if CMake is used.
   license-mole places no requirements on this identifier,
* ``DEPNAME``: A display name for the dependency, to be rendered in the output.
   The identifier will be rendered if ``DEPNAME`` is omitted.
* ``PATH``: A path relative to the project root where the dependency's files
   are located.
* ``REPOSITORY``: An HTTP/HTTPS URL to a git repository where the dependency can
   be found. This may include a path to a directory inside the repository.
* ``HOMEPAGE``: A URL to a webpage where a user can find more information about
   the dependency. This will be used when rendering the output in preference to
   ``REPOSITORY`` if both are provided. license-mole will not use this URL to
   collect license information.
* ``REVISION``: A ``commit-ish`` in the repository where the specific version of
   the dependency is found.
* ``VERSION``: A version number for the dependency. This is used for caching and
   rendering.
* ``LICENSE``: An SPDX identifier for the dependency's license.
* ``LICENSE_PATH``: A comma-separated list of URLs or paths to the text of the
   dependency's license. Paths are interpreted relative to ``REPOSITORY`` or
   ``PATH``.
* ``AUTHOR``: The dependency's author, maintainer, or packager.
* ``ATTRIBUTION``: A line of copyright attribution. If present, ``AUTHOR`` is
   ignored.

At least one of ``PATH``, ``REPOSITORY``, or ``HOMEPAGE`` is required.
Unrecognized arguments are ignored.

This format may be parsed in your own CMake functions using the
`cmake_parse_arguments
<https://cmake.org/cmake/help/latest/command/cmake_parse_arguments.html>`__
function. A simple example function::

   function(dependency)
      set(_NAME "${ARGV0}")
      cmake_parse_arguments(
         PARSE_ARGV 1
         "" ""
         "DEPNAME;PATH;VERSION;REPOSITORY;REVISION;HOMEPAGE;AUTHOR;ATTRIBUTION;LICENSE;LICENSE_PATH"
         ""
      )
      set(${_NAME}_VERSION "${_VERSION}")
      set(${_NAME}_PATH "${_PATH}")
      set(${_NAME}_REPOSITORY "${_REPOSITORY}")
      set(${_NAME}_REVISION "${_REVISION}")
   endfunction()
"""

import hashlib
import re
from typing import Any, Optional

from ..pathselector import NULLPATH, PathSelector
from ..repo import find_file_in_repo
from . import BaseScanner
from .package import BasePackage

CMAKE_CLEAN_RE = re.compile(r'\s+|#([^"]*"[^"]*")*[^"]*$')


class ManualPackage(BasePackage):
   """A description of a manual package.

   :param selector: Path selector for the file containing the definition
   :param pkg: Parsed package information
   """

   package_type = ''

   def __init__(self, selector: PathSelector, pkg: dict[str, str]):
      self.repo = pkg.get('REPOSITORY', '')
      if 'PATH' in pkg:
         path = pkg['PATH']
      else:
         rev = pkg.get('REVISION', '')
         if rev and 'github.com' in self.repo:
            path = f'{self.repo}/tree/{rev}'
         else:
            path = self.repo

      self._id = pkg['ID']
      super().__init__(
         name=pkg.get('DEPNAME', pkg['ID']),
         path=selector.to_selector(path) if path else NULLPATH,
         version=pkg.get('VERSION', ''),
         author=pkg.get('AUTHOR', ''),
         scan=bool(path and 'LICENSE_PATH' not in pkg),
      )
      self.licenses.add(pkg.get('LICENSE', ''))
      self.homepage = pkg.get('HOMEPAGE', '')

      self._pkg_attribution = None
      if 'ATTRIBUTION' in pkg:
         self._pkg_attribution = pkg['ATTRIBUTION'].split(r'\n')
         self.licenses.attribution = self._pkg_attribution

      if 'LICENSE_PATH' in pkg:
         paths = [f.strip('"\' ') for f in pkg['LICENSE_PATH'].split(',')]
         for path in paths:
            if '://' in path:
               self.licenses.add_file(path)
            else:
               path = find_file_in_repo(self.url, path)
               self.licenses.add_file(path)

      if len(self.licenses) > 1 and len(self.licenses.files) == 1:
         path = next(iter(self.licenses.files))
         self.licenses.files[path]['multi'] = True
         for ltype in self.licenses:
            self.licenses.link_file(ltype, path)

   @property
   def key(self) -> str:
      """A unique key identifying the package."""
      return f'manual::{self._id}'

   @property
   def url(self) -> str:
      """The URL to a "homepage" for the package."""
      return self.homepage or self.repo or self.path.to_absolute()

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      data = super().serialize(selector)
      data['id'] = self._id
      data['repo'] = self.repo
      if self.homepage:
         data['homepage'] = self.homepage
      if self._pkg_attribution:
         data['attribution'] = self._pkg_attribution
      return data

   def _prepopulate(self, data: dict[str, Any]):
      self._id = data['id']

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      super()._deserialize(data, selector)
      self.repo = data['repo']
      self.homepage = data.get('homepage', '')
      self._pkg_attribution = data.get('attribution')
      if self._pkg_attribution:
         self.licenses.attribution = self._pkg_attribution


class ManualScanner(BaseScanner):
   """A scanner that collects manually-specified dependency information."""

   package_type = 'manual'

   def __init__(self, group: str):
      super().__init__(group)
      self._checksums: dict[str, str] = {}

   def scan(self, path: PathSelector):
      """Scan a dependency text file for information.

      Collected packages are stored in `self.packages`.

      :param path: The path to the dependency text file
      """
      with open(path.to_absolute(), 'rb') as f:
         data = f.read()
         lines = data.decode().split('\n')
         self._checksums[path.path] = hashlib.sha256(data).hexdigest()

      in_block = False
      pkg: dict[str, Any] = {}
      # TODO: don't require newlines
      for line in lines:
         line = CMAKE_CLEAN_RE.sub(' ', line).strip()
         if not in_block and line.startswith('dependency('):
            in_block = True
            pkg['ID'] = line.split('(')[1].strip()
         elif in_block and line.startswith(')'):
            self.packages[f'manual::{pkg["ID"]}'] = ManualPackage(path, pkg)
            pkg = {}
            in_block = False
         elif in_block and line:
            key, value = line.split(' ', maxsplit=1)
            pkg[key] = value.strip('" ')

   def compare_cache(self, cache: dict[str, Any], paths: list[PathSelector]) -> bool:
      """Compare cached data to the current state.

      If this function returns True, then the cached data is considered to be
      up-to-date and the scan does not need to be re-run.

      :param cache: Data that had been previously saved in the cache
      :param paths: Absolute paths to current state
      :return: True if the cached data is up-to-date
      """
      matches = 0
      for path in paths:
         with open(path, 'rb') as f:
            sum_hash = hashlib.file_digest(f, 'sha256').hexdigest()
         if cache['!checksums'].get(path.path) == sum_hash:
            matches += 1
      return matches == len(paths)

   def deserialize_cache(self, cache: dict[str, Any], selector: PathSelector):
      """Populate the scanner with cached data.

      :param cache: The serialized data from the cache
      :param selector: The selector that paths are relative to
      """
      for key, info in cache.items():
         if key.startswith('!'):
            continue
         pkg = ManualPackage.deserialize(info, selector)
         self.packages[pkg.key] = pkg

   def serialize_cache(self, selector: PathSelector) -> Optional[dict[str, Any]]:
      """Serialize the scan results for caching.

      :param selector: The selector that paths are relative to
      :return: A dict suitable for JSON serialization
      """
      cache = {'!checksums': self._checksums}
      for key, pkg in self.packages.items():
         cache[key] = pkg.serialize(selector)
      return cache
