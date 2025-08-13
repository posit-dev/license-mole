# vim: ts=3 sts=3 sw=3 expandtab:
"""Project configuration information.

Copyright (c) 2025 Posit Software, PBC

All configuration paths are relative to the directory containing mole.toml.

Packages that do not name a repository are located relative to the default
repository path given by the "root" value in mole.toml. If "root" is not
specified, the directory containing mole.toml is also used as the path to
the default repository.

Relative paths to repositories are resolved relative to the directory
containing mole.toml.
"""

import glob
import os
import re
from typing import Any, Literal, TypedDict, Union, cast

from . import cache, logger
from . import config_format as cf
from .config_format import FORMATS as _FORMATS
from .config_format import OUTPUTS as _OUTPUTS
from .configfile import ConfigFile
from .scan.pathselector import REPO_PATHS, PathSelector


class OverrideDict(TypedDict, total=False):
   """A set of overrides for a package's metadata."""

   ignored: bool
   """If True, the package is skipped during scanning."""
   rename: str
   """Replaces the package name to unify renamed versions."""
   author: str
   """The author of the package."""
   license: tuple[str, ...]
   """SPDX-style license identifier(s)."""
   url: str
   """The URL for the package source code repository."""
   license_files: list[str]
   """Absolute paths or URLs to the text of the license."""
   attribution: list[str]
   """Copyright lines, ideally with year and author."""
   permit_license_change: bool
   """If True, this package is allowed to be consolidated into a package with different licensing attribution."""


GROUPS: dict[str, dict[str, list[PathSelector]]] = {}
COLLECTIONS: dict[str, list[str]] = {}
OVERRIDES: dict[str, OverrideDict] = {}
SPDX_OVERRIDES: dict[str, tuple[str, ...]] = {}
RELABEL: dict[str, str] = {}
# re-export
OUTPUTS = _OUTPUTS
FORMATS = _FORMATS

# A unique identifier that can't (easily) appear in a toml file
# Used to create PathSelector objects that refer to the Rust vendor cache
RUST_VENDOR = '\0RUST'

_GLOB_CACHE: dict[str, re.Pattern] = {}


def _populate_repos(root: str, repos: ConfigFile):
   """Fill the REPO_PATHS dict from the config file.

   :param root: The project root that paths are relative to
   :param repos: The [repos] section from the config file
   """
   REPO_PATHS[''] = root
   for env in repos.keys():
      default_path = repos.value(env)
      if env in os.environ:
         REPO_PATHS[env] = os.path.abspath(os.environ[env])
      elif os.path.isabs(default_path):
         REPO_PATHS[env] = default_path
      else:
         REPO_PATHS[env] = os.path.abspath(os.path.join(root, default_path))


def _populate_groups(config: ConfigFile):
   """Fill the GROUPS dict from the config file.

   :param config: The [groups] section from the config file
   """
   for scan_type in config.keys():
      GROUPS[scan_type] = {}
      group_config = config.required_group(scan_type)
      for name in group_config.keys():
         path_glob = group_config.value(name)
         if isinstance(path_glob, str):
            sel = PathSelector('', path_glob)
         else:
            sel = PathSelector(*path_glob)
            if os.path.isabs(sel.path):
               logger.warning('Absolute path "%s" specified relative to "%s".', sel.path, sel.repo)
         matches = glob.glob(sel.to_absolute())
         if not matches:
            matches = [sel.to_absolute()]
         GROUPS[scan_type][name] = [sel.to_selector(p) for p in matches]


def _type_mismatch(key: str, expected: type | tuple[type, type], actual: Any) -> str:  # noqa: ANN401
   """Format an error message for a type mismatch.

   :param key: The config key being validated
   :param expected: The expected data type
   :param actual: The unexpected value
   :return: the error message to raise
   """
   actual_name = type(actual).__name__
   if isinstance(expected, tuple):
      expected_name = f'{expected[0].__name__}[{expected[1].__name__}]'
      if isinstance(actual, list) or isinstance(actual, tuple):
         element_name = ''
         for v in actual:
            if element_name and element_name != type(v).__name__:
               element_name = 'mixed'
               break
            element_name = type(v).__name__
         actual_name = f'{type(actual).__name__}[{element_name}]'
   else:
      expected_name = expected.__name__
   return f'{key} expected {expected_name}, got {actual_name}'


_EXPECTED_TYPES: dict[str, type | tuple[type, type]] = {
   'ignored': bool,
   'rename': str,
   'author': str,
   'url': str,
   'license': (tuple, str),
   'license_files': (list, str),
   'attribution': (list, str),
   'permit_license_change': bool,
}


def _validate_override(package: str, key: str, value: Any) -> Any:  # noqa: ANN401
   """Validate and normalize an override setting.

   :param package: The package key being overridden
   :param key: The key in the override dict
   :param value: The raw value from the config file
   :raises KeyError: if the key is unrecognized
   :raises TypeError: if the value is of the wrong data type
   :return: The cleaned value
   """
   if key not in _EXPECTED_TYPES:
      raise KeyError(f'unexpected key "{key}" in override')
   expected = _EXPECTED_TYPES[key]
   if isinstance(expected, tuple):
      if isinstance(value, expected[1]):
         # single unwrapped value
         value = expected[0]([value])
      if expected[0] is tuple and isinstance(value, list):
         # translate list to tuple
         value = tuple(value)
      if not isinstance(value, expected[0]):
         raise TypeError(_type_mismatch(f"overrides.'{package}'.{key}", expected, value))
      for v in cast('tuple', value):
         if not isinstance(v, expected[1]):
            raise TypeError(_type_mismatch(f"overrides.'{package}'.{key}", expected, value))
   elif not isinstance(value, expected):
      raise TypeError(_type_mismatch(f"overrides.'{package}'.{key}", expected, value))
   return value


def _populate_overrides(overrides: ConfigFile):
   """Validate and populate the OVERRIDES dict from the config file.

   :param overrides: The [overrides] section from the config file
   """
   for key in overrides.keys():
      values = overrides.required_group(key)
      data = OverrideDict()
      for attrib in values.keys():
         data[attrib] = _validate_override(key, attrib, values.value(attrib))  # type: ignore[literal-required]
      OVERRIDES[key] = data


def _populate_spdx_overrides(overrides: ConfigFile):
   """Validate and populate the SPDX_OVERRIDES dict from the config file.

   :param overrides: The [spdx-overrides] section from the config file
   :raises TypeError: if the value is of the wrong data type
   """
   for key in overrides.keys():
      value = overrides.value(key)
      if isinstance(value, str):
         SPDX_OVERRIDES[key] = (value,)
      elif isinstance(value, list):
         for v in value:
            if not isinstance(v, str):
               raise TypeError(_type_mismatch(f"spdx-overrides.'{key}'", (list, str), value))
         SPDX_OVERRIDES[key] = tuple(value)
      else:
         raise TypeError(_type_mismatch(f"spdx-overrides.'{key}'", (list, str), value))


def _populate_collections(collections: ConfigFile):
   """Validate and populate the COLLECTIONS dict from the config file.

   :param collections: The [collections] section from the config file
   :raises KeyError: if a collection contains an unrecognized group name
   """
   if not collections:
      # If no collections are defined, imply them from the group definitions
      for group_name in GROUPS:
         COLLECTIONS[group_name] = [group_name]
   else:
      for name in collections.keys():
         group_list = collections.value(name)
         for group in group_list:
            if not any(group in g for g in GROUPS.values()):
               raise KeyError(group)
         COLLECTIONS[name] = group_list


def _resolve_cache_path(config: ConfigFile, key: str, default: str) -> str:
   """Get the path to a cache file from the config.

   :param config: The config file
   :param key: The config key
   :param default: The default filename if the key does not exist
   :return: The absolute path to the cache file
   """
   return config.relative_path(config.value(key, default))


def load_config(path: str):
   """Load configuration from a mole.toml file.

   :param path: path to configuration file
   """
   config = ConfigFile(os.path.abspath(path))
   root = config.relative_path(config.value('root', '.'))

   _populate_repos(root, config.required_group('repos'))
   _populate_groups(config.required_group('groups'))
   _populate_collections(config.group('collections'))
   _populate_overrides(config.group('overrides'))
   _populate_spdx_overrides(config.group('spdx-overrides'))
   RELABEL.update(config.value('relabel', {}))
   cf.populate_formats(config.group('formats'))
   cf.populate_outputs(config.required_group('output'))

   cache.set_web_cache_root(_resolve_cache_path(config, 'web_cache', '.mole.web_cache'))
   cache.scan_cache.load(_resolve_cache_path(config, 'scan_cache', '.mole.scan_cache.json'))
   cache.repo_cache.load(_resolve_cache_path(config, 'repo_cache', '.mole.repo_cache.json'))
   cache.license_cache.load(_resolve_cache_path(config, 'license_cache', '.mole.license_cache.json'))
   REPO_PATHS[RUST_VENDOR] = _resolve_cache_path(config, 'rust_cache', '.mole.rust_cache')


def get_overrides(pkg: str) -> OverrideDict:
   """Get a dictionary of overrides for a package based on its key.

   :param pkg: Package identifier
   :return: Known metadata overrides
   """
   override = OVERRIDES.get(pkg)
   if override:
      return override

   for key, override in OVERRIDES.items():
      if not key.endswith('*'):
         continue
      if pkg.startswith(key[:-1]):
         return override

   return {}


def get_file_overrides(path: str) -> Union[Literal[False], tuple[str, ...]]:
   """Get a license identifier to override the automatic detection.

   :param path: A path or URL to a license file
   :return: License identifier override, if known
   """
   for override_path, ltypes in SPDX_OVERRIDES.items():
      if override_path not in _GLOB_CACHE:
         pattern = override_path.replace('.', '\\.').replace('*', '.*')
         _GLOB_CACHE[override_path] = re.compile(f'^{pattern}$')
      if _GLOB_CACHE[override_path].match(path):
         return tuple(ltypes)
   return False
