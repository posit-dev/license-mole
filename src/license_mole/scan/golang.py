# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for collecting Go packages.

Copyright (c) 2025 Posit Software, PBC
"""

import hashlib
import json
import os
import re
import subprocess
from functools import cached_property
from typing import Any, Optional

from .. import repo
from . import BaseScanner, NoLicenseError
from .package import BasePackage
from .pathselector import PathSelector

VERSION_PATTERN = re.compile(r'/v\d+$')
CASE_ESCAPE = re.compile(r'!([a-z])')
GOPATH = subprocess.run(
   ['go', 'env', 'GOMODCACHE'],
   stdout=subprocess.PIPE,
   check=True,
).stdout.decode().strip() + '/'


def _hash_sumfile(path: str) -> str:
   """Hash the checksum file for a Go project.

   :param path: Path to the directory containing go.mod
   :return: Hash of sums file, or an empty string if not found
   """
   try:
      with open(os.path.join(path, 'go.sum'), 'rb') as sumfile:
         return hashlib.file_digest(sumfile, 'sha256').hexdigest()
   except FileNotFoundError:
      return ''


def _go_list(path: str) -> list[dict[str, Any]]:
   """Use `go list` to collect recursive dependency information.

   :param path: The path to the project root
   :return: A list of parsed JSON data
   """
   result = subprocess.run(
      ['go', 'list', '-deps', '-json'],
      stdout=subprocess.PIPE,
      cwd=path,
      encoding='utf8',
      check=True,
   )

   data = result.stdout
   pos = 0
   packages = []
   dec = json.JSONDecoder()

   while data:
      pkg, pos = dec.raw_decode(data)
      data = data[pos:].strip()
      packages.append(pkg)

   return packages


class GoModule:
   """A basic wrapper around the JSON response from `go list`.

   :param pkg: Parsed JSON
   """

   def __init__(self, pkg: dict[str, Any]):
      self.info = pkg
      self.path = pkg.get('Root', pkg['Dir'])
      self.is_internal = (
         pkg.get('Goroot') or
         pkg.get('Standard') or
         pkg['ImportPath'].startswith('golang.org/x') or
         False
      )
      if self.is_internal:
         self.repo = ''
         self.path = 'go_internal://'
         self.version = None
      elif 'Module' in pkg:
         self.repo = pkg['Module']['Path']
         self.version = pkg['Module'].get('Version')
         if 'Root' not in pkg and self.repo in self.path:
            # vendored, so module root may not be package root
            self.path = self.path[:self.path.index(self.repo) + len(self.repo)]
      else:
         self.repo = pkg['ImportPath']
         self.version = None


class GoPackage(BasePackage):
   """A description of a Go package.

   A package is a collection of modules deployed together under a single name.

   :param selector: Path selector for the parent package
   :param mod: Parsed package information from `go list`
   """

   package_type = 'Go'

   def __init__(self, selector: PathSelector, mod: GoModule):
      if mod.is_internal:
         self.module = 'go'
         name = 'Go standard libraries'
      else:
         self.module = mod.path.replace(GOPATH, '').split('/vendor/')[-1]
         name = self.module.split('@')[0]
         name = VERSION_PATTERN.sub('', name)
         name = '/'.join(name.split('/')[-2:])

      super().__init__(
         name=name,
         path=selector.to_selector(mod.path),
      )
      self.repo = mod.repo
      self.is_internal = mod.is_internal

   @cached_property
   def key(self) -> str:
      """A unique key identifying the package."""
      return f'go::{self.module.replace("@", "=")}'

   @cached_property
   def url(self) -> str:
      """The URL to a "homepage" for the package."""
      url = self._overrides.get('url')
      if url:
         return url

      if self.is_internal:
         return 'https://go.dev'

      url = repo.clean_repo_url('/'.join(self.repo.split('/')[:3]))
      if not url:
         raise repo.HomepageMissingError(self.module)

      return url

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      data = super().serialize(selector)
      path = selector.to_absolute(data['path'])
      if path.startswith(GOPATH):
         data['path'] = path.replace(GOPATH, 'go_internal://')
      data['repo'] = self.repo
      data['module'] = self.module
      data['internal'] = self.is_internal
      if 'license_files' in data:
         lfiles = {}
         for fn, info in data['license_files'].items():
            path = selector.to_absolute(fn)
            if path.startswith(GOPATH):
               fn = path.replace(GOPATH, 'go://')
            lfiles[fn] = info
         data['license_files'] = lfiles
      return data

   def _prepopulate(self, data: dict[str, Any]):
      self.module = data['module']

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      lfiles = {}
      for fn, info in data.get('license_files', {}).items():
         if fn.startswith('go_internal://'):
            fn = fn.replace('go_internal://', GOPATH)
         lfiles[fn] = info
      data['license_files'] = lfiles
      super()._deserialize(data, selector)
      if self.path.path.startswith('go_internal://'):
         self.path = PathSelector('', self.path.path.replace('go_internal://', GOPATH))
      self.repo = data['repo']
      self.is_internal = data['internal']


class GoScanner(BaseScanner):
   """A scanner that collects Go packages and their dependencies."""

   package_type = 'Go'

   def __init__(self, group: str):
      super().__init__(group)
      self._sums: list[str] = []

   def scan(self, path: PathSelector):
      """Scan a Go project for dependency information.

      Dependencies are collected into packages so that submodules contained
      in a single repository under a single license are presented as one
      entry for reporting.

      Collected packages are stored in `self.packages`.

      :param path: The path to the Go project root
      :raises NoLicenseError: if a package's metadata has no licensing data
      """
      abspath = path.to_absolute()
      for mod_info in _go_list(abspath):
         mod = GoModule(mod_info)

         if mod.path == abspath:
            # first-party package, not a third-party dependency
            continue

         find_key = 'go::go' if mod.is_internal else mod.path
         if find_key in self.packages:
            # already have a representative
            continue

         pkg = GoPackage(path, mod)
         if pkg.ignored:
            continue
         if pkg.licenses.is_empty():
            if 'github.com/rstudio' in mod.path or '/src/go' in mod.path:
               # internal package without a license, no need to disclose
               continue
            raise NoLicenseError(pkg.key)
         self.packages[pkg.key] = pkg

      self._sums.append(_hash_sumfile(abspath))

   def compare_cache(self, cache: dict[str, Any], paths: list[PathSelector]) -> bool:
      """Compare cached data to the current state.

      If this function returns True, then the cached data is considered to be
      up-to-date and the scan does not need to be re-run.

      :param cache: Data that had been previously saved in the cache
      :param paths: Absolute paths to current state
      :return: True if the cached data is up-to-date
      """
      if '!sums' not in cache:
         # No cached lockfile checksums
         return False
      sums = set(cache['!sums'])
      for path in paths:
         sum_hash = _hash_sumfile(path.to_absolute())
         if not sum_hash:
            continue
         if sum_hash not in sums:
            return False
         sums.remove(sum_hash)
      return not sums

   def deserialize_cache(self, cache: dict[str, Any], selector: PathSelector):
      """Populate the scanner with cached data.

      :param cache: The serialized data from the cache
      :param selector: The selector that paths are relative to
      """
      for key, info in cache.items():
         if key.startswith('!'):
            continue
         pkg = GoPackage.deserialize(info, selector)
         self.packages[pkg.key] = pkg

   def serialize_cache(self, selector: PathSelector) -> Optional[dict[str, Any]]:
      """Serialize the scan results for caching.

      :param selector: The selector that paths are relative to
      :return: A dict suitable for JSON serialization
      """
      cache: dict[str, Any] = {'!sums': [s for s in self._sums if s]}
      for key, pkg in self.packages.items():
         cache[key] = pkg.serialize(selector)
      return cache
