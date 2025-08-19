# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for collecting npm packages.

Copyright (c) 2025 Posit Software, PBC
"""

import glob
import hashlib
import json
import subprocess
from functools import cached_property
from os.path import basename, dirname, exists
from os.path import join as path_join
from typing import Any, Optional, Union

from .. import cache, logger, repo
from ..errors import MissingPackageError, NoLicenseError
from ..pathselector import PathSelector
from . import BaseScanner
from .package import BasePackage


def _get_node_modules_path(path: str, package: Optional[str] = None) -> str:
   """Find the node_modules folder containing a package's dependencies.

   Optionally, can find the specific node_modules folder containing a specific
   dependency. If the dependency is not found, returns the folder where the
   NpmScanner class will install it. Note that this may not be where a real
   build would choose to put it.

   :param path: Path to the directory containing package.json
   :param package: The name of a specific dependency to locate
   :return: The absolute path to node_modules, if found
   """
   parent = path
   while len(parent) > 1:
      node_modules = path_join(parent, 'node_modules')
      check_path = path_join(node_modules, package, 'package.json') if package else node_modules
      if exists(check_path):
         return node_modules

      parent = dirname(parent)
      if basename(parent) == 'node_modules':
         parent = dirname(parent)

   if package:
      # not found, find where it's likely to get installed
      return _get_node_modules_path(path)

   return ''


def _find_lockfile(path: str) -> str:
   """Find the lockfile for an npm project.

   This will recurse up the directory tree. While this is not how a normal
   npm installation works, it is necessary to accommodate a project that is
   installed as part of a workspace.

   :param path: Path to the directory containing package.json
   :return: Path to the lockfile, or an empty string if not found
   """
   parent = path
   while len(parent) > 1:
      for fn in ['npm-shrinkwrap.json', 'package-lock.json', 'yarn.lock']:
         lockfile = path_join(parent, fn)
         if exists(lockfile):
            return lockfile
      parent = dirname(parent)
   return ''


def _hash_lockfile(path: str) -> str:
   """Hash the lockfile for an npm project.

   :param path: Path to the directory containing package.json
   :return: Hash of lockfile
   :raises FileNotFound: if no lockfile can be found
   """
   lock = _find_lockfile(path)
   if not lock:
      raise FileNotFoundError(path_join(path, 'package-lock.json'))
   with open(lock, 'rb') as lockfile:
      return hashlib.file_digest(lockfile, 'sha256').hexdigest()


def _parse_repository(repo_data: Union[str, dict[str, str]]) -> str:
   """Extract a URL from the 'repository' property in package.json.

   :param repo_data: The 'repository' structure
   :return: The repository URL, or an empty string if not found
   """
   if isinstance(repo_data, str):
      return repo.clean_repo_url(repo_data)
   if repo_data.get('type') == 'git':
      return repo.clean_repo_url(repo_data['url'])
   return ''


def _collect_authors(pkg: dict[str, Any]) -> str:
   """Collect the author/maintainers attribute from package.json.

   :param pkg: The parsed package.json file
   :return: An author/maintainer label
   """
   author = pkg.get('author', '')
   if isinstance(author, dict):
      author = author['name']

   if not author:
      maintainers = []
      for maintainer in pkg.get('maintainers', []):
         maintainers.append(
            maintainer['name'] if isinstance(maintainer, dict) else maintainer,
         )
      if maintainers:
         author = ', '.join(maintainers)
   return author


class NpmPackage(BasePackage):
   """A description of an npm package.

   The constructor loads package.json and collects relevant information.

   :ivar package_json: The parsed contents of package.json

   :param path: Path to the directory containing package.json
   :raises MissingPackageError: if package.json cannot be loaded
   """

   package_type = 'NPM'

   def __init__(self, path: PathSelector):
      pkg_json = path.to_absolute('package.json')
      try:
         with open(pkg_json, 'r', encoding='utf8') as f:
            pkg = json.load(f)
      except FileNotFoundError as e:
         raise MissingPackageError(None) from e

      self.pkg_name = pkg.get('name', basename(path.path))
      if pkg.get('private'):
         if 'quarto' in path.path and self.pkg_name != 'quarto':
            self.pkg_name = f'$quarto/{self.pkg_name}'

      super().__init__(
         name=pkg.get('displayName', self.pkg_name),
         path=path,
         version=pkg.get('version', ''),
         author=_collect_authors(pkg),
      )
      self.package_json = pkg

      if 'license' not in self._overrides:
         licenses = self.package_json.get('licenses', [self.package_json.get('license', '')])
         for l in licenses:
            if isinstance(l, str):
               self.licenses.add(l)
               continue
            if l['type'] != 'BSD':
               # don't add unqualified BSD, it's ambiguous
               self.licenses.add(l['type'])
            if not self.licenses.files and 'github.com' in l.get('url', ''):
               try:
                  self.licenses.add_file(l['url'])
               except ValueError:
                  # Just log if a license file isn't found. We'll find another source for
                  # it later or ask for an override.
                  logger.warning('Explicit license file "%s" not found for %s', l['url'], self.key)

   @cached_property
   def key(self) -> str:
      """A unique key identifying the package."""
      return f'npm::{self.pkg_name}={self.version}'

   @cached_property
   def url(self) -> str:
      """The URL to a "homepage" for the package."""
      url = self._overrides.get('url')
      if url:
         return url
      url = cache.repo_cache.get(self.key, '')
      if not url and 'repository' in self.package_json:
         url = _parse_repository(self.package_json['repository'])
      if not url and 'homepage' in self.package_json:
         url = self.package_json['homepage']
      if not url:
         url = f'https://npmjs.com/package/{self.name}/v/{self.version}'
      cache.repo_cache.set(self.key, url)
      return url

   @cached_property
   def workspaces(self) -> list[str]:
      """The list of workspaces found in package.json."""
      return self.package_json.get('workspaces', [])

   @cached_property
   def dependencies(self) -> list[str]:
      """The list of direct dependencies, as npm version atoms."""
      return list(self.package_json.get('dependencies', {}).keys())

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      data = {
         **super().serialize(selector),
         'pkg_name': self.pkg_name,
      }
      if self.package_json.get('repository'):
         data['repository'] = self.package_json['repository']
      if self.package_json.get('homepage'):
         data['homepage'] = self.package_json['homepage']
      return data

   def _prepopulate(self, data: dict[str, Any]):
      self.pkg_name = data['pkg_name']

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      super()._deserialize(data, selector)
      # Technically inaccurate but will contain the parts that matter
      self.package_json = data


class NpmScanner(BaseScanner):
   """A scanner that collects npm packages and their dependencies."""

   package_type = 'NPM'

   def __init__(self, group: str):
      super().__init__(group)
      self._locks: list[str] = []

   def scan(self, path: PathSelector):
      """Entry point for scanning a package tree.

      :param path: The root of the package tree
      """
      pkg = NpmPackage(path)
      self._scan_recursive(path, pkg)
      self._locks.append(_hash_lockfile(path.to_absolute()))

   def _scan_recursive(self, path: PathSelector, pkg: NpmPackage):  # noqa: DOC201
      """Load an npm package and collect its dependencies.

      This function operates recursively to collect transitive dependencies.
      If the node_modules directory cannot be found, it invokes `npm install`
      to create it. This may not have the same behavior as a real build, so
      please disregard any modified lockfiles. (It shouldn't need to do this
      if run in a repo after a build has been completed.)

      Dev dependencies are omitted under the assumption that we won't be
      redistributing their contents. Peer dependencies and optional
      dependencies are omitted under the assumption that they will be
      explicitly depended upon in another package.

      If a package declares workspaces, those workspaces will also be scanned
      for dependencies.

      :param path: Path to the directory containing package.json
      :param pkg: A pre-parsed package object, if available
      :raises MissingPackageError: if a dependency cannot be resolved
      """
      if pkg.name and not pkg.package_json.get('private') and not pkg.ignored:
         # Don't output private/ignored packages but do check their dependencies
         self.packages[pkg.key] = pkg

      if not pkg.workspaces and not pkg.dependencies:
         # package has no runtime dependencies
         return

      abspath = path.to_absolute()

      node_modules = _get_node_modules_path(abspath)
      if not node_modules:
         logger.info('node_modules not found, running npm install in %s', abspath)
         subprocess.run(
            ['npm', 'install', '--omit=dev'],
            cwd=abspath,
            check=True,
         )
         node_modules = _get_node_modules_path(abspath)

      for ws in pkg.workspaces:
         for ws_path in glob.glob(path.to_absolute(ws)):
            if not exists(path_join(ws_path, 'package.json')):
               logger.debug('Workspace %s not found for %s, skipping', ws_path, pkg.key)
               continue
            ws_sel = path.to_selector(ws_path)
            ws_pkg = NpmPackage(ws_sel)
            self._scan_recursive(ws_sel, ws_pkg)

      for dep_name in pkg.dependencies:
         if dep_name.startswith('@types/'):
            # We'll also be depending on the main package
            continue
         dep_nm_path = _get_node_modules_path(node_modules, dep_name)
         dep_path = path_join(dep_nm_path, dep_name)
         try:
            self.collect_deps(path.to_selector(dep_path))
         except MissingPackageError as e:
            if e.args[0] is None:
               raise MissingPackageError(f'Unable to resolve {dep_name} in {pkg.name}') from e
            raise MissingPackageError(f'While resolving {pkg.name}:\n\t{e.args[0]}') from e.__cause__

   def collect_deps(self, path: PathSelector):  # noqa: DOC201
      """Load package.json and scan child dependencies.

      This function will skip packages that have already been loaded.

      :param path: Path to the directory containing package.json
      :raises NoLicenseError: if the package has no license information
      """
      pkg = NpmPackage(path)
      if pkg.key in self.packages:
         # This package has already been loaded
         return

      if pkg.ignored:
         # package is marked as ignored in overrides
         return

      if pkg.licenses.is_empty():
         raise NoLicenseError(pkg.key)

      self.packages[pkg.key] = pkg

      # Recursively check dependencies
      self._scan_recursive(path, pkg)

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
         locks.remove(lock_hash)
      return not locks

   def deserialize_cache(self, cache: dict[str, Any], selector: PathSelector):
      """Populate the scanner with cached data.

      :param cache: The serialized data from the cache
      :param selector: The selector that paths are relative to
      """
      for key, info in cache.items():
         if key.startswith('!'):
            continue
         pkg = NpmPackage.deserialize(info, selector)
         self.packages[pkg.key] = pkg

   def serialize_cache(self, selector: PathSelector) -> Optional[dict[str, Any]]:
      """Serialize the scan results for caching.

      :param selector: The selector that paths are relative to
      :return: A dict suitable for JSON serialization
      """
      cache: dict[str, Any] = {'!locks': self._locks}
      for key, pkg in self.packages.items():
         cache[key] = pkg.serialize(selector)
      return cache
