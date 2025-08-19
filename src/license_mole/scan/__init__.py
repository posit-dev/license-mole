# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for analyzing and validating license information on packages.

Copyright (c) 2025 Posit Software, PBC
"""

import glob
import os
from typing import Any, Callable, Iterator, NamedTuple, Optional

from .. import logger
from ..cache import scan_cache
from ..errors import LicenseConflictError, LicenseValidationError, UnidentifiedLicenseError
from ..licenses import licenses, scan_repo_for_license
from ..pathselector import PathSelector
from .package import BasePackage

SCANNERS: dict[str, 'type[BaseScanner]'] = {}


class BaseScanner:
   """Abstract base class for package scanners.

   :ivar group: The name of the package group populated by this scanner
   :ivar packages: The packages collected by this scanner
   :ivar cache_data: Data loaded from the cache, to be used to ensure stable
      results across runs
   :cvar package_type: A descriptive label for the type of packages found by
      this scanner

   :param name: The name for a group of packages
   """

   package_type = ''

   group: str
   packages: dict[str, BasePackage]
   cache_data: dict[str, Any]

   def __init__(self, name: str):
      self.group = name
      self.packages = {}
      self.cache_data = {}

   def scan(self, path: PathSelector):  # noqa: DOC501
      """Scan for dependencies for a specified project.

      Implementations should store their findings in self.packages.
      The definition of a "project root" may vary by scanner.

      :param path: A project root directory
      """
      raise NotImplementedError()

   def compare_cache(self, cache: dict[str, Any], paths: list[PathSelector]) -> bool:  # noqa: ARG002
      """Compare cached data to the current state.

      If this function returns True, then the cached data is considered to be
      up-to-date and the scan does not need to be re-run.

      The default implementation returns False.

      :param cache: Data that had been previously saved in the cache
      :param paths: Path selectors to current state
      :return: True if the cached data is up-to-date
      """
      return False

   def deserialize_cache(self, cache: dict[str, Any], selector: PathSelector):  # noqa: B027
      """Populate the scanner with cached data.

      If cached data is present, this function will be called even if the
      `compare_cache` function returns False and even if a complete scan
      is forced. Implementations may use this information to ensure stable
      outputs across runs.

      The default implementation does nothing.

      :param cache: The serialized data from the cache
      :param selector: The selector that paths are relative to
      """

   def serialize_cache(self, selector: PathSelector) -> Optional[dict[str, Any]]:  # noqa: ARG002
      """Serialize the scan results for caching.

      The definition of the cached data is scanner-specific, but it should
      include sufficient data to identify if the current state of the
      repository has changed from the cached state.

      The default implementation returns None, which disables caching.

      :param selector: The selector that paths are relative to
      :return: A dict suitable for JSON serialization
      """
      return None


class _PackageItem(NamedTuple):
   scanner: BaseScanner
   paths: list[PathSelector]


def _iterate_packages(
   scanner_class: type[BaseScanner],
   groups_to_scan: dict[str, list[PathSelector]],
) -> Iterator[_PackageItem]:
   for group, path_selectors in groups_to_scan.items():
      if not path_selectors:
         continue
      base: PathSelector = path_selectors[0]
      pkg_paths = [glob.glob(s.to_absolute()) for s in path_selectors]
      selectors: list[PathSelector] = []
      for ps in pkg_paths:
         selectors.extend(base.to_selector(p) for p in ps)
      if not selectors:
         if base.repo and not os.environ.get(base.repo):
            logger.error(
               'Use the %s environment variable to override the path for %s group "%s".',
               base.repo,
               scanner_class.package_type,
               group,
            )
         raise FileNotFoundError(f'No packages found matching {base.to_absolute()}')
      scanner = scanner_class(group)
      yield _PackageItem(scanner, selectors)


def _root_key(paths: list[PathSelector]) -> list[str]:
   """Produce a root key to tell if the path selectors have changed.

   :param paths: Path selectors to reference
   :return: A serializable list
   """
   if not paths:
      return []
   key: list[str] = [p.path for p in paths]
   if paths[0].repo:
      key.insert(0, paths[0].repo)
   return key


def check_cache(
   scanner_class: type[BaseScanner],
   groups_to_scan: dict[str, list[PathSelector]],
) -> bool:
   """Look for package updates that might require rendering.

   :param scanner_class: Class to be used to scan for dependencies
   :param groups_to_scan: Mapping from group names to path globs
   :return: True if the cache is up-to-date
   """
   for scanner, pkg_paths in _iterate_packages(scanner_class, groups_to_scan):
      cached_data = scan_cache.get(scanner.package_type, scanner.group)
      if not cached_data:
         return False
      root_key = _root_key(pkg_paths)
      if root_key != cached_data.get('!root'):
         return False
      if not scanner.compare_cache(cached_data, pkg_paths):
         return False
   return True


def scan_groups(
   scanner_class: type[BaseScanner],
   groups_to_scan: dict[str, list[PathSelector]],
   force: bool = False,
) -> dict[str, dict[str, BasePackage]]:
   """Search a set of paths for packages and their dependencies.

   :param scanner_class: Class to be used to recursively load dependencies
      which stores the packages it finds in its .packages property
   :param groups_to_scan: Mapping from group names to path globs
   :param force: If True, scan even if the cache is up to date
   :return: A dictionary of package groups. Each package group is a dictionary
      mapping package identifiers to a descriptor object.
   """
   groups = {}
   for scanner, pkg_paths in _iterate_packages(scanner_class, groups_to_scan):
      if not pkg_paths:
         # Empty group, skip
         continue
      root_key = _root_key(pkg_paths)
      cached_data = scan_cache.get(scanner.package_type, scanner.group)
      clean = not force and cached_data and cached_data.get('!root') == root_key
      clean = clean and scanner.compare_cache(cached_data, pkg_paths)
      if clean:
         logger.debug('Using cached %s dependencies for %s.', scanner_class.package_type, scanner.group)
         scanner.deserialize_cache(cached_data, pkg_paths[0])
      else:
         logger.info('Collecting %s dependencies for %s...', scanner_class.package_type, scanner.group)
         scanner.cache_data = cached_data
         for path in pkg_paths:
            scanner.scan(path)
         cached_data = scanner.serialize_cache(pkg_paths[0]) or {}
         if cached_data:
            cached_data['!root'] = root_key
            scan_cache.set(scanner.package_type, scanner.group, cached_data)
      groups[scanner.group] = scanner.packages

   return groups


def _run_pass(pass_index: int, pkgs: list[BasePackage], pass_fn: Callable[[BasePackage], bool]) -> list[BasePackage]:
   """Run an analysis pass repeatedly until it doesn't make progress.

   :param pass_index: Pass number to be rendered in status messages
   :param pkgs: Packages to be analyzed
   :param pass_fn: Function to analyze each package.
      It should return True if the package's licensing is fully resolved, or
      False if the package needs further analysis.
   :return: Packages with unresolved licensing
   """
   next_pass = [pkg for pkg in pkgs if not pkg.ignored]
   licenses_linked = -1
   pass_count = 0
   while licenses_linked != 0:
      this_pass = next_pass
      next_pass = []
      licenses_linked = 0
      for dep in this_pass:
         if pass_fn(dep):
            licenses_linked += 1
         else:
            next_pass.append(dep)
      pass_count += 1
      if licenses_linked > 0:
         logger.info(
            'Pass %d.%d: identified licenses for %d/%d packages',
            pass_index,
            pass_count,
            licenses_linked,
            len(this_pass),
         )
   return next_pass


def _first_pass(dep: BasePackage) -> bool:
   """First analysis pass.

   This pass takes the following steps:

   * If no license files were auto-detected and no license identifiers are
     in the package metadata, try to download license files from the
     repository.

   * Trigger an auto-link (see LicenseCollection.auto_link_files)

   :param dep: Package to analyze
   :return: Whether the package's licensing is fully resolved
   """
   if dep.licenses.is_empty():
      logger.debug('Scanning %s for license information...', getattr(dep, 'repo', dep.url))
      path = scan_repo_for_license(dep.url)
      if path:
         dep.licenses.add_file(path)

   return dep.licenses.auto_link_files()


def _second_pass(dep: BasePackage) -> bool:
   """Second analysis pass.

   This pass takes the following steps:

   * Try to heuristically guess at the license type for each file

   * Trigger an auto-link (see LicenseCollection.auto_link_files)

   * Adds license type(s) to package metadata if none are specified

   :param dep: Package to analyze
   :raises UnidentifiedLicenseError: if a license cannot be uniquely identified
   :return: Whether the package's licensing is fully resolved
   """
   for fn, info in dep.licenses.unlinked_files.items():
      # Look up license checksums to see if we can tell what they are
      ltype = licenses.get_type_by_checksum(info['checksum']) or info['guess']
      if ltype and dep.licenses.has(ltype):
         # The file has a single detectable type that would match the package
         dep.licenses.link_file(ltype, fn)
         licenses.add(ltype, info, dep.key)

   num_ltypes, num_files = dep.licenses.count_unlinked()
   if num_ltypes > 0 and num_files > 0:
      dep.licenses.auto_link_files()
      num_ltypes, num_files = dep.licenses.count_unlinked()

   if num_ltypes == 0 and num_files > 0:
      # license file indicates license omitted from metadata
      for fn, info in dep.licenses.unlinked_files.items():
         if info['spdx']:
            dep.licenses.add(info['spdx'])
            continue

         ltype = licenses.get_type_by_checksum(info['checksum']) or info['guess']
         if ltype:
            if dep.key.startswith('npm::') and not dep.licenses.has(ltype):
               logger.warning('%s missing license %s in package.json, found in %s', dep.key, ltype, fn)
            elif dep.key.startswith('rust::') and not dep.licenses.has(ltype):
               logger.warning('%s missing license %s in Cargo.toml, found in %s', dep.key, ltype, fn)
            dep.licenses.add(ltype)
            dep.licenses.link_file(ltype, fn)
         elif not info['multi']:
            # Files containing multiple licenses are identified, just not uniquely
            raise UnidentifiedLicenseError(dep.key, fn)
         else:
            # A multi-license file exists alongside a full set of identified license files.
            # Since we can't be sure if it's actually linked to ALL of them, link it to a
            # distinct label for special rendering.
            dep.licenses.link_file('multi', fn)

   return sum(dep.licenses.count_unlinked()) == 0


def _third_pass(dep: BasePackage) -> bool:
   """Third analysis pass.

   This pass takes the following steps:
   * Heuristically links a file containing multiple licenses to identifiers
   * Tries to download missing license files from source code repository
   * Attaches a "clean" license file (if known) for unlinked identifiers

   :param dep: Package to analyze
   :raises LicenseConflictError: if the content of a license file doesn't match the spdx identifier
   :return: Whether the package's licensing is fully resolved
   """
   path: Optional[str]

   num_ltypes, num_files = dep.licenses.count_unlinked()

   if num_ltypes > 1 and num_files == 1:
      # assume that the file contains multi-license information
      path = next(iter(dep.licenses.unlinked_files.keys()))
      for ltype in dep.licenses.unlinked_ltypes:
         dep.licenses.link_file(ltype, path)
      return True

   if num_ltypes == 1:
      ltype = dep.licenses.unlinked_ltypes[0]
      path = licenses.get_file_for_type(ltype)
      if not path:
         path = scan_repo_for_license(dep.url)
      if not path:
         # Maybe a later pass will find it
         # If not, the validation step will show an error
         return False
      info = dep.licenses.add_file(path)
      if not dep.licenses.auto_link_files():
         raise LicenseConflictError(
            ltype,
            (dep.key, dep.path.to_absolute()),
            '/'.join(info['spdx']) if info['spdx'] else info['guess'] or '(none)',
            (dep.key, path),
         )
      return True

   if num_ltypes > 0 and num_files == 0:
      for ltype in dep.licenses:
         source = licenses.get_file_for_type(ltype, dep.licenses.attribution)
         if source:
            dep.licenses.add_file(source)
            dep.licenses.link_file(ltype, source)

   return sum(dep.licenses.count_unlinked()) == 0


def detect_licenses(pkgs: list[BasePackage]) -> list[BasePackage]:
   """Run analysis passes to detect licensing information for packages.

   :param pkgs: Packages to analyze
   :return: Packages that could not be fully resolved
   """
   # First pass: auto-link the easy cases
   next_pass = _run_pass(1, pkgs, _first_pass)

   # Second pass: handle packages with multiple licenses and/or files
   next_pass = _run_pass(2, next_pass, _second_pass)

   # Third pass: fill in missing license text from Github or from a "clean" copy of the license
   return _run_pass(3, next_pass, _third_pass)


def validate_licenses(pkgs: list[BasePackage]):
   """Validate the licensing on a list of packages and log problems.

   :param pkgs: Packages to validate
   :raises LicenseValidationError: if any packages failed validation
   """
   has_error = False
   logger.info('Validating licenses for %d packages...', len(pkgs))
   for dep in pkgs:
      if dep.ignored:
         continue

      num_ltypes, num_files = dep.licenses.count_unlinked()

      if len(dep.licenses) == 0:
         has_error = True
         logger.error('No license types found for %s (%s)', dep.key, dep.path.to_absolute())

      if num_ltypes:
         has_error = True
         logger.error(
            'Licenses type(s) %s missing text in %s (%s)',
            ', '.join(dep.licenses.unlinked_ltypes),
            dep.key,
            dep.path.to_absolute(),
         )

      if num_files:
         has_error = True
         logger.error('Could not detect license type for files in %s (%s)', dep.key, dep.path.to_absolute())
         for fn in dep.licenses.unlinked_files:
            logger.error('\t%s', fn)

      if not dep.licenses.links:
         has_error = True
         logger.error('No license links for %s (%s)', dep.key, dep.path.to_absolute())

      if not dep.licenses.attribution:
         has_error = True
         logger.error('No attribution for %s (%s)', dep.key, dep.path.to_absolute())

   if has_error:
      raise LicenseValidationError()


def get_scanners() -> dict[str, type[BaseScanner]]:
   """Late-load the scanner classes into SCANNERS.

   :return: The scanner dictionary
   """
   if not SCANNERS:
      from . import golang, manual, npm, rust  # noqa: PLC0415
      SCANNERS['npm'] = npm.NpmScanner
      SCANNERS['go'] = golang.GoScanner
      SCANNERS['rust'] = rust.RustScanner
      SCANNERS['manual'] = manual.ManualScanner
   return SCANNERS
