#!/usr/bin/env python3
# vim: ts=3 sts=3 sw=3 expandtab:
"""License scanner for Posit Workbench.

Copyright (c) 2025 Posit Software, PBC

Recursively collects dependendencies and groups them by component.
Generates NOTICE / NOTICE-SUPPLEMENT Markdown documentation.

NOTE: This script may install npm packages differently than the build scripts
do. Please do not commit any lockfiles that may be modified.

NOTE: This script is not suitable for use in CI. It performs quite a bit of
network traffic. This can be very slow, especially with Savannah repositories,
which are known to be flaky. To mitigate this problem, all downloads are cached
(see ``web_cache`` in ``mole.toml``). Delete this directory to purge the cache.

License analysis is cached based on package lock files and the results are
stored in a scan cache file (see ``scan_cache`` in ``mole.toml``). (This file
should be tracked.) Modified lock files will cause a rescan of the affected
groups. To force a new scan of all dependencies, pass the --force-scan flag to
this script.

To quickly check if the scan cache is up-to-date with the package lock files,
pass --check. This script will exit with an error if a scan needs to be
performed, so this can be used as a CI check or precommit hook.

To speed up the process of iterating on the Markdown formatting, the license
parsing results are cached in license_cache.json. (This file is .gitignored.)
Use the --render-only flag to use this cached data.

Set the environment variable DEBUG to enable verbose logging.

You may need to configure a GitHub PAT in ~/.netrc for some dependencies.
See https://go.dev/doc/faq#git_https for more information.
"""
import argparse
import logging
import os
import sys
from typing import Optional

from . import __version__, errors, logger, scan
from .cache import license_cache, scan_cache
from .config import COLLECTIONS, GROUPS, OUTPUTS, load_config
from .render import NoticeRenderer, RenderGroup
from .scan import BasePackage, rust


class LicenseMoleApplication:
   """The driver for the license-mole CLI application."""

   args: argparse.Namespace
   """The parsed command-line arguments."""
   collections: dict[str, list[BasePackage]]
   """Scanned packages, organized by collection."""
   render_groups: dict[str, RenderGroup]
   """Preprocessed packages, organized by group."""

   def __init__(self):
      self.args = argparse.Namespace()
      self.collections = {}
      self.render_groups = {}

   def validate_args(self) -> bool:
      """Check the command-line arguments for errors.

      :return: True if there are no errors.
      """
      self.args.output = [name.strip() for name in self.args.output]
      output_error = False
      for name in self.args.output:
         if name not in OUTPUTS:
            output_error = True
            logger.error('Unknown document: %s', name)
      if output_error:
         logger.error('Documents defined in mole.toml: %s', ' '.join(OUTPUTS.keys()))
      return not output_error

   def check_cache(self) -> int:
      """Compare the cached license information against the package lock files.

      Returns 0 if the cache is up-to-date.

      :return: An error code (0 for success)
      """
      clean = True
      for type_name, scanner_class in scan.get_scanners().items():
         if not scanner_class:
            continue
         if not scan.check_cache(scanner_class, GROUPS[type_name]):
            clean = False
            break
      if clean:
         logger.info('Package dependency cache is up-to-date.')
         return 0
      logger.error('Package dependency cache requires updating.')
      cache_path = os.path.relpath(scan_cache.cache_path, start=self.args.ROOT)
      logger.error(f'Please scan for new dependencies and commit {cache_path}.')
      return 1

   def _scan_all_groups(self):
      """Scan all groups for license data."""
      groups: dict[str, dict[str, BasePackage]] = {}
      all_packages: list[BasePackage] = []

      for type_name, scanner_class in scan.get_scanners().items():
         if not scanner_class:
            continue
         group_set = scan.scan_groups(scanner_class, GROUPS.get(type_name, {}), self.args.force_scan)
         for group_name, contents in group_set.items():
            group_packages = groups.get(group_name, {})
            group_packages.update(contents)
            groups[group_name] = group_packages

      for group_name, contents in groups.items():
         all_packages.extend(contents.values())
         assigned = False
         for name, selected_groups in COLLECTIONS.items():
            if group_name in selected_groups:
               self.collections[name].extend(contents.values())
               assigned = True
         if not assigned:
            logger.error('Package group %s not assigned to a collection', group_name)
            # TODO: make this an exception
            sys.exit(1)

      logger.info('Beginning validation check...')
      scan.detect_licenses(all_packages)
      scan.validate_licenses(all_packages)

   def run_scan(self) -> int:
      """Scan the project for license information.

      :return: An error code (0 for success)
      """
      try:
         self._scan_all_groups()
         self.render_groups = {k: RenderGroup(k, v) for k, v in self.collections.items()}
         for k, v in self.render_groups.items():
            license_cache.set(k, v.to_dict())
         license_cache.save()
         return 0
      except errors.NoLicenseError as e:
         logger.error('No license information found for %s', e.key)
         logger.error('If necessary, add data to the [overrides] configuration section.')
      except errors.LicenseConflictError as e:
         logger.error('Conflicting license types detected:')
         logger.error('\tPrevious: %s (from %s in %s)', e.ltype, e.source[0], e.source[1])
         logger.error('\tNew:      %s (from %s in %s)', e.new_ltype, e.new_source[0], e.new_source[1])
         logger.error('Determine which license is correct and add it in the [overrides] configuration section.')
      except errors.LicenseValidationError:
         logger.error('Consider adding missing information in the [overrides] configuration section.')
      except errors.UnidentifiedLicenseError as e:
         logger.error('Could not identify license file %s for %s', e.path, e.key)
         logger.error('Specify the license codes for this package in the [overrides] configuration section.')
      except errors.MissingPackageError as e:
         msg_lines = str(e).split('\n')
         for line in msg_lines:
            logger.error(line)
         logger.info('You may need to install this package.')
      except errors.HomepageMissingError as e:
         logger.error('Could not find homepage for package %s', e.key)
         logger.error('Add a repository pattern to the [repos] configuration section, or')
         logger.error('add a URL for this package in the [overrides] configuration section.')
      except rust.PackageGroupConflictError as e:
         logger.error('Rust package %s has uncertain subpackage grouping.', e.name)
         logger.error(' First group: %s', ', '.join(e.group1.licenses.attribution))
         logger.error(' Subpackages: %s', ', '.join(e.group1.children))
         logger.error('Second group: %s', ', '.join(e.group2.licenses.attribution))
         logger.error(' Subpackages: %s', ', '.join(e.group2.children))
         logger.error('Specify how these should be handled using the [rust.group] configuration section')
         logger.error('or a "rename" directive in the [overrides] configuration section.')
      return 1

   def load_license_cache(self) -> int:
      """Load cached scan results from disk.

      :return: An error code (0 for success)
      """
      logger.info('Using cached dependency information.')
      for k, v in license_cache.items():
         self.render_groups[k] = RenderGroup(k, v)
      return 0

   def render_outputs(self) -> int:
      """Render license documents from scanned license data.

      :return: An error code (0 for success)
      """
      outputs = self.args.output or list(OUTPUTS)
      for output_name in outputs:
         output = OUTPUTS[output_name]
         renderer = NoticeRenderer(output, list(self.render_groups.values()))
         renderer.write(output['destination'])
      return 0

   def main(self, argv: Optional[list[str]] = None) -> int:
      """Entry point for running license-mole from the command line.

      :param argv: The list of command-line arguments
      :return: Status code (0 for success)
      """
      parser = argparse.ArgumentParser(
         prog='license-mole',
         description='Multi-language Open-source License Excavator',
      )
      parser.add_argument(
         '--version', '-v',
         action='store_true',
         help='Show current version of license-mole',
      )
      parser.add_argument(
         '--render-only',
         action='store_true',
         help='Do not scan, render from cached data only',
      )
      parser.add_argument(
         '--force-scan', '-f',
         action='store_true',
         help='Scan all dependencies, even if cache is up-to-date',
      )
      parser.add_argument(
         '--check', '-c',
         action='store_true',
         help='Quickly verify cached data against package lock files',
      )
      parser.add_argument(
         '--output', '-o',
         action='append',
         default=[],
         help='Output a specific document, may be specified multiple times (default: all documents)',
      )
      # parser.add_argument(
      #    '--generate', '-g',
      #    action='store_true',
      #    help='Generate an initial configuration file',
      # )
      parser.add_argument(
         'ROOT',
         default=os.getcwd(),
         nargs='?',
         help='Path to project root containing mole.toml (default: working directory))',
      )

      self.args = parser.parse_args(argv)
      if self.args.version:
         print(f'license-mole version {__version__}')
         return 0
      load_config(os.path.join(self.args.ROOT, 'mole.toml'))
      if not self.validate_args():
         return 1
      if self.args.check:
         return self.check_cache()
      self.collections = {k: [] for k in COLLECTIONS}
      if self.args.render_only:
         status = self.load_license_cache()
      else:
         status = self.run_scan()
      if status:
         return status
      return self.render_outputs()


def main() -> int:
   """Entry point for license-mole.

   :return: Status code (0 for success)
   """
   logging.basicConfig(
      level=logging.DEBUG if os.environ.get('DEBUG') else logging.INFO,
      format='[%(levelname)s] %(message)s',
   )
   app = LicenseMoleApplication()
   return app.main()


if __name__ == '__main__':
   sys.exit(main())
