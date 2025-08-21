# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for collecting Rust packages.

Copyright (c) 2025 Posit Software, PBC
"""

import glob
import hashlib
import os
import subprocess
import tomllib
from functools import cached_property
from typing import Any, Optional, cast

from .. import logger, repo
from ..config import RUST_GROUP, RUST_VENDOR, get_overrides
from ..errors import HomepageMissingError, NoLicenseError
from ..licenses import find_license_files
from ..licenses.parse import analyze_license_file
from ..pathselector import PathSelector
from . import BaseScanner
from .manual import ManualPackage
from .package import BasePackage, version_tuple

# TODO: document better
"""
# If the auto-detection is worried about combining packages and you want to
# combine them, name them here and identify which package is representative.
RUST_GROUP = {}

# If the auto-detection is worried about combining packages and you want to
# keep them separate them, provide a disambiguating name for one package here.
# moved to overrides.rename
"""


def _hash_lockfile(path: str) -> str:
   """Hashes the lockfile for a Rust project.

   :param path: Path to the directory containing Cargo.toml
   :return: Hash of lockfile
   :raises FileNotFound: if no lockfile can be found
   """
   parent = path
   while len(parent) > 1:
      lockpath = os.path.join(parent, 'Cargo.lock')
      if os.path.exists(lockpath):
         break
      parent = os.path.dirname(parent)
   if len(parent) <= 1:
      raise FileNotFoundError(os.path.join(path, 'Cargo.lock'))
   with open(lockpath, 'rb') as lockfile:
      return hashlib.file_digest(lockfile, 'sha256').hexdigest()


class PackageGroupConflictError(RuntimeError):
   """Raised when distinct package groups have the same name.

   :param name: The name of the package group
   :param group1: The packages contained within the first group
   :param group2: The packages contained within the second group
   """

   def __init__(self, name: str, group1: 'RustPackage', group2: 'RustPackage'):
      super().__init__('Conflict in grouping packages')
      self.name = name
      self.group1 = group1
      self.group2 = group2


class RustBasicPackage:
   """A basic wrapper around the "package" section of Cargo.toml.

   :param path: Path to directory containing Cargo.toml
   :param pkg: Parsed TOML
   """

   def __init__(self, path: str, pkg: dict[str, Any]):
      self.path = path
      self.info = pkg
      self.name = pkg.get('name', '')
      self.license = pkg.get('license', '')
      self.readme = pkg.get('readme', '')
      if 'authors' in pkg:
         self.author = ', '.join(pkg['authors'])
      else:
         self.author = pkg.get('author', '')
      self.version = pkg.get('version', '')
      self.version_tuple = version_tuple(self.version)
      self.repo = repo.clean_repo_url(pkg.get('repository', ''))
      self.attribution: list[str] = []

      overrides = get_overrides(f'rust::{self.name}')
      self._rename = overrides.get('rename', '')
      if self._rename:
         self.name = self._rename

      if 'attribution' in overrides:
         self.attribution = overrides['attribution']
      else:
         # Pre-collect the attribution from the license file(s) so that we don't
         # risk grouping packages with different authors
         license_files = find_license_files(path)
         for file in license_files:
            info = analyze_license_file(file, self.author)
            for attr in sorted(info['attribution'], key=lambda a: (len(a), a)):
               # If this line is a substring of any existing line, use the existing line
               # The loop is sorted in order of decreasing length to make this work better
               if not any(attr in a for a in self.attribution):
                  self.attribution.append(attr)
         self.attribution = sorted(self.attribution)

   @cached_property
   def combine_key(self) -> tuple[str, str, str, str]:
      """Returns a key that identifies if packages can be merged."""
      # If no copyright attribution can be found, fall back to the author's name
      attrib = ' '.join(self.attribution) or self.author
      return (self.repo, self.license, attrib, self._rename)


def _cargo_vendor(path: str) -> dict[str, RustBasicPackage]:
   """Use `cargo vendor` to collect recursive dependency information.

   :param path: The path to the project root
   :return: A dictionary mapping dependency paths to parsed TOML data
   """
   target_name = os.path.basename(path)
   if not target_name:
      target_name = os.path.basename(os.path.dirname(path))
   destdir = PathSelector(RUST_VENDOR, target_name)
   if not os.path.exists(destdir):
      # If the vendor cache already exists, don't re-run it
      # TODO: force flag?
      subprocess.run(
         [
            'cargo',
            'vendor',
            '-q',
            '--respect-source-config',
            '--versioned-dirs',
            '--locked',
            destdir,
         ],
         stdout=subprocess.DEVNULL,
         stderr=subprocess.DEVNULL,
         cwd=path,
         check=True,
      )

   packages: dict[str, RustBasicPackage] = {}
   for cargo_toml in sorted(glob.glob(destdir.to_absolute('*/Cargo.toml'))):
      with open(cargo_toml, 'rb') as f:
         pkg_info = tomllib.load(f)['package']

      # If two packages have the same name but different versions, use the newer version.
      pkg = RustBasicPackage(os.path.dirname(cargo_toml), pkg_info)
      if pkg.name in packages:
         v1 = pkg.version_tuple
         v2 = packages[pkg.name].version_tuple
         if v1 < v2:
            continue
      packages[pkg.name] = pkg

   return packages


class RustPackage(BasePackage):
   """A description of a Rust package group.

   A package group may be a single Cargo package, or multiple packages stored
   within the same repository. This grouping was chosen to reduce repetition
   in internal dependencies.

   :param pkgs: Parsed package information
   """

   package_type = 'Rust'

   def __init__(self, pkgs: list[RustBasicPackage]):
      # rep = representative package
      if len(pkgs) > 1:
         repo_url = pkgs[0].repo.rstrip('/')
         name = repo_url.split('/')[-1]
         rep = [*(p for p in pkgs if p.name == name), *pkgs][0]
      else:
         name = pkgs[0].name
         rep = pkgs[0]

      self.combine_key = rep.combine_key

      super().__init__(
         name=name,
         path=PathSelector('', rep.path),
         author=rep.author,
         version=rep.version,
      )
      self.children = [p.name for p in pkgs]
      self.licenses.add(rep.license)
      self.repo = self._overrides.get('url', rep.repo)
      self._attribution = self._overrides.get('attribution', rep.attribution)
      if self._attribution:
         # We did special parsing earlier to clean this up
         self.licenses.attribution = self._attribution

   @cached_property
   def key(self) -> str:
      """A unique key identifying the package."""
      return f'rust::{self.name}'

   @cached_property
   def url(self) -> str:
      """The URL to a "homepage" for the package."""
      if not self.repo:
         raise HomepageMissingError(self.name)
      return self.repo

   def merge(self, other: 'RustPackage'):
      """Merge the children of two packages.

      :param other: The other package
      """
      self.children.extend(child for child in other.children if child not in self.children)

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      data = super().serialize(selector)
      data['repo'] = self.repo
      data['ltype'] = self.combine_key[1]
      data['attribution'] = self._attribution
      if self.combine_key[3]:
         data['rename'] = self.combine_key[3]
      data['children'] = self.children
      return data

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      super()._deserialize(data, selector)
      self.repo = data['repo']
      # pylint: disable=protected-access
      self._attribution = data['attribution']
      if self._attribution:
         self.licenses.attribution = self._attribution
      self.combine_key = (data['repo'], data['ltype'], data['attribution'], data.get('rename', ''))
      self.children = data['children']


class RustScanner(BaseScanner):
   """A scanner that collects Rust packages and their dependencies."""

   package_type = 'Rust'

   def __init__(self, group: str):
      super().__init__(group)
      self._locks: set[str] = set()

      self.packages['rust::rust'] = ManualPackage(
         PathSelector('', ''),
         {
            'ID': 'rust',
            'DEPNAME': 'Rust standard libraries',
            'REPOSITORY': 'https://github.com/rust-lang/rust',
            'LICENSE': 'Apache-2.0 OR MIT',
            'LICENSE_PATH': 'https://github.com/rust-lang/rust/raw/master/COPYRIGHT',
            'ATTRIBUTION': 'Copyright (c) The Rust Project Contributors',
         },
      )

   def scan(self, path: PathSelector) -> None:
      """Scan a Rust project for dependency information.

      Dependencies are collected into packages so that submodules contained
      in a single repository under a single license are presented as one
      entry for reporting.

      Collected packages are stored in `self.packages`.

      :param path: The path to the Rust project root
      :raises NoLicenseError: if a package's metadata has no licensing data
      """
      combined = {}
      abspath = path.to_absolute()
      if os.path.isfile(abspath):
         if os.path.basename(abspath) == 'Cargo.toml':
            # If the config points to a Cargo.toml file, point at the directory instead
            abspath = os.path.dirname(abspath)
         else:
            logger.warning('%s is not a directory, skipping.', abspath)
            return
      for bpkg in _cargo_vendor(abspath).values():
         if bpkg.combine_key not in combined:
            combined[bpkg.combine_key] = [bpkg]
         else:
            combined[bpkg.combine_key].append(bpkg)

      for pkgs in combined.values():
         pkg = RustPackage(pkgs)
         if pkg.ignored:
            continue
         if pkg.licenses.is_empty():
            raise NoLicenseError(pkg.key)
         if pkg.key in self.packages:
            # Package already detected, decide what to do
            existing = cast('RustPackage', self.packages[pkg.key])
            if pkg.combine_key == existing.combine_key:
               # Safe to unify
               existing.merge(pkg)
               continue
            old = set(existing.children)
            new = set(pkg.children)
            if not old.issubset(new) and not new.issubset(old):
               pkg = self._resolve(existing, pkg)
         self.packages[pkg.key] = pkg

      self._locks.add(_hash_lockfile(abspath))

   def _resolve(self, old: RustPackage, new: RustPackage) -> RustPackage:
      """Decide how to deal with two conflicting packages.

      This function will mutate one or both packages.

      :param old: The previous detected package
      :param new: The new detected package
      :raises PackageGroupConflictError: if child packages have incompatible
         license/attribution metadata
      :return: The merged package, or the modified package to keep separate
      """
      if all(RUST_GROUP.get(child) == new.name for child in old.children):
         old.merge(new)
         return old
      if all(RUST_GROUP.get(child) == old.name for child in new.children):
         new.merge(old)
         return new
      raise PackageGroupConflictError(old.key, old, new)

   def compare_cache(self, cache: dict[str, Any], paths: list[PathSelector]) -> bool:
      """Compare cached data to the current state.

      If this function returns True, then the cached data is considered to be
      up-to-date and the scan does not need to be re-run.

      :param cache: Data that had been previously saved in the cache
      :param paths: Absolute paths to current state
      :return: True if the cached data is up-to-date
      """
      if '!locks' not in cache:
         # No cached lockfile checksums
         return False
      locks = set(cache['!locks'])
      for path in paths:
         lock_hash = _hash_lockfile(path.to_absolute())
         if lock_hash not in locks:
            return False
      return True

   def deserialize_cache(self, cache: dict[str, Any], selector: PathSelector):
      """Populate the scanner with cached data.

      :param cache: The serialized data from the cache
      :param selector: The selector that paths are relative to
      """
      for key, info in cache.items():
         if key.startswith('!'):
            continue
         pkg = RustPackage.deserialize(info, selector)
         self.packages[pkg.key] = pkg

   def serialize_cache(self, selector: PathSelector) -> Optional[dict[str, Any]]:
      """Serialize the scan results for caching.

      :param selector: The selector that paths are relative to
      :return: A dict suitable for JSON serialization
      """
      cache: dict[str, Any] = {'!locks': list(self._locks)}
      for key, pkg in self.packages.items():
         if key == 'rust::rust':
            continue
         cache[key] = pkg.serialize(selector)
      return cache
