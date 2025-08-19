# vim: ts=3 sts=3 sw=3 expandtab:
"""Exception classes used across license-mole.

Copyright (c) 2025 Posit Software, PBC
"""

from typing import Optional


class LicenseConflictError(RuntimeError):
   """Error raised when a license file disagrees with existing information.

   :param ltype: Identifier of known license
   :param source: Package and file where known license was found
   :param new_ltype: Identifier of newly-found license
   :param new_source: Package and file containing newly-found license
   """

   def __init__(self, ltype: str, source: tuple[str, str], new_ltype: str, new_source: tuple[str, str]):
      super().__init__('Conflicting license types')
      self.ltype = ltype
      self.source = source
      self.new_ltype = new_ltype
      self.new_source = new_source


class MissingPackageError(RuntimeError):
   """Error raised when a named dependency can't be found.

   :param msg: Description of the dependency chain leading to the missing package
   """

   def __init__(self, msg: Optional[str]):
      super().__init__(msg)


class NoLicenseError(RuntimeError):
   """Error raised when package metadata does not contain license information.

   :param key: Package identifier
   """

   def __init__(self, key: str):
      super().__init__('No license information found')
      self.key = key


class LicenseValidationError(RuntimeError):
   """Error raised while validating licenses.

   This can be caused by failing to find license text for a license type,
   failing to identify the license type for a license file, or failing to
   identify copyright attribution for a package.
   """

   def __init__(self):
      super().__init__('License validation error')


class UnidentifiedLicenseError(RuntimeError):
   """Error raised when a package's licensing cannot be identified.

   For this exception to be raised, the package must not have any license
   identifiers in its metadata, it must have a license file, and the
   heuristics cannot identify the license file.

   :param key: Package identifier
   :param path: Full path to license file
   """

   def __init__(self, key: str, path: str):
      super().__init__('Unidentified license')
      self.key = key
      self.path = path


class HomepageMissingError(RuntimeError):
   """Error raised when a package's homepage cannot be resolved.

   :param key: package identifier
   """

   def __init__(self, key: str):
      super().__init__('Could not find homepage for package')
      self.key = key
