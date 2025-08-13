# vim: ts=3 sts=3 sw=3 expandtab:
"""Recursive configuration file handling.

Copyright (c) 2025 Posit Software, PBC
"""

import os
from typing import Any, KeysView, Optional

import tomllib as toml


# TODO: come up with a way to define a schema
class ConfigFile:
   """Wrapper around a recursive dictionary."""

   def __init__(self, path: Optional[str], data: Optional[dict[str, Any]] = None):
      self._path = path or ''
      self._config: dict[str, Any] = {}
      if data is not None:
         self._config = data
      elif path is not None:
         with open(path, 'rb') as f:
            self._config = toml.load(f)

   def __bool__(self) -> bool:
      return bool(self._path)

   def __contains__(self, key: str) -> bool:
      return key in self._config

   def value(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
      """Return a value from the config file.

      :param key: Dictionary key.
      :param default: If the key is not found, this is returned instead.
      :return: The data that was stored in the dictionary.
      """
      if key in self._config:
         return self._config[key]
      return default

   def group(self, key: str) -> 'ConfigFile':
      """Return a child group from the config file.

      If a requested sub-dictionary is found to be a string, it is treated as a
      path relative to the current config file, and the contents of that file are
      used instead.

      If the key does not exist, an empty :py:class:`ConfigFile` is returned.

      :param key: Dictionary key.
      :return: The contents of the named group.
      """
      if key not in self._config:
         return ConfigFile(None)
      contents = self._config[key]
      if isinstance(contents, str):
         return ConfigFile(self.relative_path(contents))
      return ConfigFile(self._path, contents)

   def required_group(self, key: str) -> 'ConfigFile':
      """Return a required child group from the config file.

      Uses the same behavior as :py:meth:`group`, but raises an exception if
      the group is not defined.

      :param key: Dictionary key.
      :raises KeyError: if the key is not defined.
      :return: The contents of the named group.
      """
      contents = self.group(key)
      if not contents:
         raise KeyError(key)
      return contents

   def relative_path(self, path: str) -> str:
      """Construct an absolute path to a file relative to this one.

      If the path is absolute, it is returned unmodified.

      :param path: The relative path to resolve
      :return: An absolute path
      """
      if os.path.isabs(path):
         return path
      return os.path.join(os.path.dirname(self._path), path)

   def keys(self) -> KeysView[str]:
      """Return the list of keys in the current group.

      :return: The list of keys
      """
      return self._config.keys()
