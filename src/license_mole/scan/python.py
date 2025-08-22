# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for collecting Python packages.

Copyright (c) 2025 Posit Software, PBC
"""

import hashlib
import json
import re
import tomllib
from typing import Any, Callable, NamedTuple, Optional

from ..cache import download_file_cached
from ..pathselector import PathSelector
from . import BaseScanner
from .package import BasePackage, VersionKey, version_tuple

ATOM_RE = re.compile(r'^([^ =<>!\[]+)\s*(?:(\[[^\]]+\])?\s*((?:(?:<|<=|>|>=|==|!=)\s*[^<>=\s,]+\s*(?:,|$))*))?\s*$')
VERSION_RE = re.compile(r'(<|<=|>|>=|==|!=)\s*([^<>=\s]+)$')


class _ParsedAtom(NamedTuple):
   name: str
   versions: list[tuple[str, str]]
   extra: list[str]
   provides: list[str]


def _parse_atom(atom: str) -> _ParsedAtom:
   if ';' in atom:
      atom, attr = atom.split(';')
   else:
      attr = ''
   match = ATOM_RE.match(atom.replace('(', '').replace(')', ''))
   if not match:
      raise ValueError(f'Unparseable version atom: "{atom}"')

   name, extra_str, version_str = match.groups()
   extra = []
   if extra_str:
      extra = [e.strip() for e in extra_str.strip('[]').split(',')]

   versions = []
   for version in version_str.split(','):
      if not version:
         continue
      match = VERSION_RE.match(version.strip())
      if not match:
         raise ValueError(f'Unparseable version "{version}" in atom: "{atom}"')
      versions.append((match[1], match[2]))

   provides: list[str] = []
   if 'extra' in attr:
      attr = attr.replace(' and ', ' or ')
      parts = attr.split(' or ')
      for part in parts:
         if 'extra' not in part or '==' not in part:
            continue
         part = part.split('==')[1].strip()
         part = part.split(' ')[0].strip('"\'')
         provides.append(part)
   return _ParsedAtom(name, versions, extra, provides)


def _make_predicate(op: str, version: str, chain: Callable[[VersionKey], bool]) -> Callable[[VersionKey], bool]:
   compare = version_tuple(version)
   if op == '!=':
      return lambda v: chain(v) and v != compare
   elif op == '>=':
      return lambda v: chain(v) and v >= compare
   elif op == '>':
      return lambda v: chain(v) and v > compare
   elif op == '<=':
      return lambda v: chain(v) and v <= compare
   elif op == '<':
      return lambda v: chain(v) and v < compare
   raise ValueError(f'Unknown predicate {op}')


def _select_version(versions: list[tuple[str, str]], available: Optional[list[str]] = None) -> str:
   predicate = lambda _: True
   guess = ''
   for op, version in versions:
      if op == '==':
         return version
      elif op in {'<=', '>='}:
         guess = version
      predicate = _make_predicate(op, version, predicate)
   for version in reversed(available or []):
      if predicate(version_tuple(version)):
         return version
   return guess


def _collect_releases(release_data: dict[str, list[dict[str, Any]]]) -> list[str]:
   releases: list[str] = []
   for v, release_list in release_data.items():
      for release in release_list:
         if release.get('yanked'):
            continue
         releases.append(v)
         break
   return releases


class PythonPackage(BasePackage):
   """A description of a manual package.

   :param atom: A version atom that refers to the dependency
   :param lock_version: The version number from the lockfile
   """

   package_type = 'Python'

   def __init__(self, atom: _ParsedAtom, lock_version: Optional[str] = None):
      name, versions, extra, _ = atom
      version = ''
      if lock_version:
         version = lock_version
         pypi_url = f'https://pypi.python.org/pypi/{name}/{lock_version}/json'
      else:
         pypi_url = f'https://pypi.python.org/pypi/{name}/json'

      raw_data = download_file_cached(
         pypi_url,
         headers={'Accept': 'application/json'},
      )
      data = json.loads(raw_data)
      if not version and 'releases' in data:
         version = _select_version(versions, _collect_releases(data['releases']))
      if not version:
         version = _select_version(versions)

      project = data['info'].get('project_urls', {})
      path = project.get('Source', project.get('Code', ''))
      if not path and 'Homepage' in project:
         path = project['Homepage']
      if not path and 'home_page' in data['info']:
         path = data['info']['home_page']
      if not path:
         path = data['info']['package_url']

      super().__init__(
         name=name,
         path=PathSelector('', path),  # TODO
         version=version,
         author=data['info'].get('author', data['info'].get('author_email', '')),
      )

      if 'licenses' not in self._overrides:
         ltype = data['info'].get('license')
         if ltype:
            self.licenses.add(ltype)

      self.dependencies: list[_ParsedAtom] = []
      for req in data['info'].get('requires_dist') or []:
         dep = _parse_atom(req)
         if not dep.provides or any(marker in extra for marker in dep.provides):
            self.dependencies.append(dep)

      # if 'license_files' not in self._overrides:
      #    files = data['info'].get('license_files', [])
      #    for f in files:
      #       self.licenses.add_file(self.path.to_absolute(f))

   @property
   def key(self) -> str:
      """A unique key identifying the package."""
      if self.version:
         return f'py::{self.name}=={self.version}'
      return f'py::{self.name}'

   @property
   def url(self) -> str:
      """The URL to a "homepage" for the package."""
      return self.path.to_absolute()

   def serialize(self, selector: PathSelector) -> dict[str, Any]:
      """Serialize the package for caching.

      :param selector: The selector that paths are relative to
      :return: A JSON-compatible dict of package metadata.
      """
      data = super().serialize(selector)
      return data

   def _deserialize(self, data: dict[str, Any], selector: PathSelector):
      super()._deserialize(data, selector)


class PythonScanner(BaseScanner):
   """A scanner that collects manually-specified dependency information."""

   package_type = 'Python'

   def __init__(self, group: str):
      super().__init__(group)
      self._checksums: dict[str, str] = {}
      self._lock: dict[str, str] = {}

   def scan(self, path: PathSelector):
      """Scan a Python project for dependency information.

      Collected packages are stored in `self.packages`.

      :param path: The path to the directory containing pyproject.toml
      """
      with open(path.to_absolute('pyproject.toml'), 'rb') as f:
         data = tomllib.load(f)

      try:
         lockpath = path.to_absolute('poetry.lock')
         with open(lockpath, 'rb') as f:
            lockdata = f.read()
            lockfile = tomllib.loads(lockdata.decode())
         self._checksums[path.to_relative('poetry.lock')] = hashlib.sha256(lockdata, usedforsecurity=False).hexdigest()
         self._parse_poetry(lockfile)
      except FileNotFoundError:
         pass
         # TODO: other lockfile formats
         # with open(path.to_absolute('requirements.txt'), 'r', encoding='utf-8') as f:
         #    lockfile = _parse_requirements(f.read())

      for atom in data['project'].get('dependencies'):
         self._scan_dependency(_parse_atom(atom))

   def _scan_dependency(self, atom: _ParsedAtom):
      pkg = PythonPackage(atom, self._lock.get(atom.name))
      if pkg.key in self.packages:
         return

      self.packages[pkg.key] = pkg

      for dep in pkg.dependencies:
         self._scan_dependency(dep)

   def _parse_poetry(self, lockfile: dict[str, Any]):
      for pkg in lockfile.get('package', []):
         groups = pkg.get('groups') or []
         if not groups or 'main' in groups:
            self._lock[pkg['name']] = pkg['version']

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
         # TODO: other lock types
         for fn in ['poetry.lock']:
            locktype = ''
            if path.to_relative(fn) in cache['!checksums']:
               locktype = fn
         if not locktype:
            continue
         with open(path.to_absolute(locktype), 'rb') as f:
            sum_hash = hashlib.file_digest(f, 'sha256').hexdigest()
         if cache['!checksums'].get(path.to_relative(locktype)) == sum_hash:
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
         pkg = PythonPackage.deserialize(info, selector)
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
