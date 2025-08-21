# vim: ts=3 sts=3 sw=3 expandtab:
"""A class to refer to files across a set of repositories.

Copyright (c) 2025 Posit Software, PBC
"""

import os
from typing import Iterable, NamedTuple, Optional, Union

REPO_PATHS: dict[Optional[str], str] = {}


class PathSelector(NamedTuple):
   """A resolved group root selector.

   :ivar repo: The environment variable used to find the repository
   :ivar path: The absolute path to the selected path in the repository
   """

   repo: str
   path: str

   def to_absolute(self, path: str = '.') -> str:
      """Return the absolute path to a file in the repository.

      If the input is a URL or not a relative path, it is returned unchanged.
      Paths are interpreted relative to the selected path.

      :param path: A path relative to the selected path
      :raises ValueError: if this selector is a URL
      :return: An absolute path
      """
      if '://' in self.path:
         if path == '.':
            return self.path
         raise ValueError('Cannot find paths relative to a URL selector')
      if '://' in path or os.path.isabs(path):
         return path
      return os.path.realpath(os.path.abspath(os.path.join(REPO_PATHS[self.repo], self.path, path)))

   def to_relative(self, path: str) -> str:
      """Return the relative path to a file in the repository.

      If the input is a URL or not an absolute path, it is returned unchanged.
      The returned paths is relative to the repository root.

      :param path: An absolute path
      :return: A relative path
      """
      if '://' in path or not os.path.isabs(path):
         return path
      return os.path.relpath(path, start=REPO_PATHS[self.repo])

   def to_selector(self, path: str) -> 'PathSelector':
      """Return a new PathSelector for another path in the same repository.

      Paths are interpreted relative to the repository root.

      :param path: An absolute path, relative path, or URL
      :return: A selector for that path
      """
      if '://' in path:
         return PathSelector('', path)
      return PathSelector(self.repo, self.to_relative(path))

   @property
   def simplified(self) -> Union[str, list[str]]:
      """A simplified form of the selector.

      Paths in the default repo are returned as a string.
      Paths in an alternate repo are returned as a list.
      """
      if self.repo:
         return [self.repo, self.path]
      return self.path

   def __fspath__(self) -> str:
      if not self:
         raise ValueError(self.path)
      return self.to_absolute()

   def __bool__(self) -> bool:
      return self != NULLPATH

   @staticmethod
   def parse(value: Union[str, Iterable[str]]) -> 'PathSelector':
      """Parse a value (perhaps from a config file) into a PathSelector.

      :param value: A serialized representation of a path selector
      :raises TYpeError: if the value cannot be converted to a PathSelector
      :return: The path selector
      """
      try:
         if isinstance(value, str):
            if value.startswith('@/'):
               return PathSelector('@', value[2:])
            return PathSelector('', value)
         parts: list[str] = []
         for part in value:
            if not isinstance(part, str):
               raise TypeError()
            parts.append(part)
         if len(parts) != 2:  # noqa: PLR2004
            raise TypeError()
         return PathSelector(parts[0], parts[1])
      except TypeError:
         raise TypeError('PathSelector expects str or [str, str]') from None


NULLPATH = PathSelector('', 'null://')
