# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for organizing multiple versions of packages.

Copyright (c) 2025 Posit Software, PBC
"""

from typing import TYPE_CHECKING, Iterator, Optional, TypedDict, Union

from ..config_format import FormatDict
from ..licenses.parse import analyze_license_file
from ..scan.package import VersionKey, version_tuple
from .package import RenderPackage, WithRepresentative, attribution_comparison_key

if TYPE_CHECKING:
   from . import NoticeRenderer


class VersionCompareKey(TypedDict):
   """Typing for version comparison keys."""

   ltype: list[str]
   attr: set[str]
   file: list[str]


def _version_compare_keys(pkg: RenderPackage) -> VersionCompareKey:
   """Produce a version comparison key for a package.

   :param pkg: The package to compare
   :return: A comparison key
   """
   return {
      'ltype': sorted(pkg.licenses.keys()),
      'attr': set(attribution_comparison_key(pkg.attribution)),
      # pass in a dummy author to avoid warnings; we don't care about it
      'file': [analyze_license_file(path, 'n/a')['checksum'] for path in pkg.licenses.values()],
   }


class VersionGroup(WithRepresentative):
   """A description of multiple versions of a package.

   Versions are grouped based on matching licenses and attribution.

   :param packages: The packages contained within this group
   :raises ValueError: if the package list is empty
   """

   force_versions: bool = False
   """If True, always render package versions."""

   def __init__(self, packages: list[RenderPackage]):
      if not packages:
         raise ValueError('Empty package list')
      self.version_groups: list[list[RenderPackage]] = []
      self._last_compare: Optional[VersionCompareKey] = None
      for pkg in sorted(packages):
         self._add_package(pkg)

   def __bool__(self) -> bool:
      """Return False if no packages are in the group."""
      return all(len(group) > 0 for group in self.version_groups)

   def __iter__(self) -> Iterator[list[RenderPackage]]:
      """Iterate over the version groups."""
      return iter(group for group in self.version_groups)

   def __contains__(self, other: RenderPackage) -> bool:
      """Return True if the package is already in the group."""
      for group in self.version_groups:
         if any(pkg.key == other.key for pkg in group):
            return True
      return False

   @property
   def representative(self) -> RenderPackage:
      """Gets the package that represents the group as a whole."""
      return self.version_groups[0][0]

   @property
   def name(self) -> str:
      """Gets the name from a representative package."""
      return self.representative.render_name

   @property
   def key(self) -> str:
      """Gets the package key for this group."""
      return self.representative.unversioned

   @property
   def url(self) -> str:
      """Gets the homepage/repo URL for this group."""
      return self.representative.url

   @property
   def sort_key(self) -> list[Union[str, VersionKey]]:
      """A key for sorting version groups.

      This key will sort first in order of ascending package name, then in
      order of descending most recent version.
      """
      key: list[Union[str, VersionKey]] = [self.name.replace('@', '').upper()]
      for group in self.version_groups:
         for pkg in group:
            key.append(tuple(-p if isinstance(p, int) else p for p in version_tuple(pkg.version)))
      return key

   def _add_package(self, pkg: RenderPackage) -> None:
      if not self.version_groups or not self._last_compare:
         self._last_compare = _version_compare_keys(pkg)
         self.version_groups.append([pkg])
         return
      if pkg in self:
         return
      changed, new_compare = self._detect_license_change(pkg, self._last_compare)
      if changed:
         self._last_compare = new_compare
         self.version_groups.append([])
      self.version_groups[-1].append(pkg)
      pkg.version_groups.append(self)

   def _detect_license_change(
      self,
      pkg: RenderPackage,
      prev: VersionCompareKey,
   ) -> tuple[bool, VersionCompareKey]:
      """Check to see if the package was relicensed between versions.

      For correct results, call this function from newest to oldest.

      :param pkg: The next package to compare
      :param prev: The comparison key for the previous package
      :return: If there was a relicensing, and the next compare state
      """
      compare = _version_compare_keys(pkg)
      if pkg.permit_license_change:
         return False, prev
      if compare['ltype'] != prev['ltype']:
         # License explicitly changed
         return True, compare
      if not compare['attr'].issubset(prev['attr']):
         # Attribution changed by more than just new contributors
         return True, compare
      unmatched = set(compare['file'])
      for cs in prev['file']:
         if cs not in unmatched:
            # License not found in current package
            return True, compare
         unmatched.discard(cs)
      if unmatched:
         # Current package has new license file
         return True, compare
      return False, compare

   def clone(self, exclude: set[str]) -> Optional['VersionGroup']:
      """Create a copy of this version group.

      :param exclude: A set of package keys to exclude from the copy
      :return: A deep copy of the group referencing the same packages
      """
      # initialize with a temporary list that will get overridden
      packages: list[RenderPackage] = []
      for group in self:
         packages.extend(pkg for pkg in group if pkg.key not in exclude)
      if not packages:
         return None
      return VersionGroup(packages)

   def _merge_one(self, vgrp: list[RenderPackage], other: list[RenderPackage], exclude: set[str]):
      """Merge a group from another object into a group from this one.

      :param vgrp: Destination package group
      :param other: Package group to be merged
      :param exclude: Package names (not keys) to omit while merging
      """
      for other_pkg in other:
         if other_pkg.name in exclude or any(other_pkg.key == pkg.key for pkg in vgrp):
            # explicitly excluded or already included
            continue
         vgrp.append(other_pkg)
      vgrp.sort()

   def merge(self, other: 'VersionGroup', exclude: set[str]):
      """Merge another version group into this one.

      :param other: Another version group for the same package
      :param exclude: A set of package keys to ignore
      """
      all_packages = []
      for vgrp in self:
         all_packages.extend(vgrp)
      for vgrp in other:
         all_packages.extend(vgrp)
      all_packages.sort()
      self._last_compare = None
      self.version_groups = []
      for pkg in all_packages:
         if pkg.key not in exclude:
            self._add_package(pkg)

   def render_summary(self, fmt: FormatDict) -> list[str]:
      """Render a Markdown summary of the packages in the group.

      There will be one line for each version group.

      :param fmt: Description of the rendering format
      :return: A list of one-line summaries
      """
      if len(self.version_groups) == 1 and not self.force_versions:
         return [self.version_groups[0][0].render(fmt, [])]
      lines = []
      for group in self:
         versions = [pkg.version for pkg in group if pkg.version]
         lines.append(group[0].render(fmt, versions))
      return lines

   def render_long(self, fmt: FormatDict, context: 'NoticeRenderer') -> list[str]:
      """Render complete attribution in Markdown for the packages in the group.

      :param fmt: Description of the rendering format
      :param context: An object containing shared information
      :return: A list of rendered Markdown sections
      """
      lines = []
      for group in self:
         if len(self.version_groups) > 1 or self.force_versions:
            versions = [pkg.version for pkg in group if pkg.version]
         else:
            versions = []
         lines.append(group[0].render_long(fmt, versions, context))
      return lines
