# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for compiling and rendering notice files.

Copyright (c) 2025 Posit Software, PBC
"""

import re
from itertools import groupby
from typing import Any, Union

from .. import logger
from ..config_format import FORMATS, OUTPUTS, DocumentDict, FormatDict
from ..licenses import licenses as license_registry
from ..licenses import normalize_ltype_for_comparison
from ..licenses.parse import analyze_license_file
from ..markdown import auto_hyperlink, strip_markdown
from ..scan.package import BasePackage
from .labels import LICENSE_NAMES
from .package import LicenseContext, RenderPackage, populate_template
from .package import attribution_comparison_key as attribution_comparison_key
from .versiongroup import VersionGroup

INTERP_PLACEHOLDER = re.compile(r'%\(([^)]+)\)s')


class RenderGroup:
   """A description of a functional group of packages.

   The name of the group will be used as the interpolation key when rendering
   the Markdown template file.

   :param group_name: The name of the functional group.
   :param packages: The packages in the group.
   """

   def __init__(self, group_name: str, packages: Union[list[BasePackage], list[dict[str, Any]]]):
      self.name = group_name

      self.packages: list[RenderPackage] = []
      combined: dict[str, RenderPackage] = {}
      for pkg in packages:
         if getattr(pkg, 'ignored', False):
            continue
         # Make a deep copy of the package because we will mutate it
         rpkg = RenderPackage(pkg, group_name)
         if rpkg.combined:
            if rpkg.render_name in combined:
               combined[rpkg.render_name].merge(rpkg)
               continue
            combined[rpkg.render_name] = rpkg
         self.packages.append(rpkg)
      self.packages.sort()

      self.groups = [
         VersionGroup(list(g))
         for _, g in groupby(self.packages, lambda pkg: pkg.unversioned)
      ]

   def __bool__(self) -> bool:
      return len(self.packages) > 0

   def to_dict(self) -> list[dict[str, Any]]:
      """Serialize the group.

      :return: A dictionary suitable for JSON serialization
      """
      return [pkg.to_dict() for pkg in self.packages]

   def render_summary(self, fmt: FormatDict, context: LicenseContext) -> list[str]:
      """Render the summary for each package in the group.

      :param fmt: Description of the rendering format
      :param context: An object containing shared information
      :return: A list of Markdown texts
      """
      self.groups.sort(key=lambda g: g.name.replace('@', '').upper())
      lines = []
      for vgroup in self.groups:
         if vgroup.key in context.excluded:
            continue
         lines.extend(vgroup.render_summary(fmt))
      return lines


class NoticeRenderer(LicenseContext):
   """A class to render the licensing information for a group of packages.

   :param output: Description of the document to be generated
   :param groups: The RenderGroups to be included
   """

   def __init__(self, output: DocumentDict, groups: list[RenderGroup]):
      super().__init__(FORMATS[output['format']])
      self.groups = groups
      self.packages: dict[str, VersionGroup] = {}
      self._output = output
      self._sections: dict[str, str] = {}
      self._included: set[str] = set()

      # Identify which groups are used by the template
      with open(self._output['template'], 'r', encoding='utf8') as f:
         self._used_sections = INTERP_PLACEHOLDER.findall(f.read())
         for section in self._used_sections:
            self._sections[section] = ''

      # Packages to be excluded
      if 'exclude' in output:
         other = NoticeRenderer(OUTPUTS[output['exclude']], groups)
         self.excluded = self._collect_excluded(other.packages)

      for rgrp in groups:
         for pkg in rgrp.packages:
            self._collect_licenses(pkg)
         for vgrp in rgrp.groups:
            if rgrp.name in self._used_sections:
               self._included.add(vgrp.name)
            if vgrp.name in self.packages:
               self.packages[vgrp.name].merge(vgrp, self.excluded)
            else:
               new_vgrp = vgrp.clone(self.excluded)
               if new_vgrp:
                  self.packages[vgrp.name] = new_vgrp

      if 'shared-licenses' in self._used_sections:
         for ltype, usage in sorted(self.license_usage.items()):
            clean_path = license_registry.get_file_for_type(ltype)
            if len(usage) <= 1 or not clean_path:
               continue
            self.shared_licenses[ltype] = clean_path

   def _collect_excluded(self, groups: dict[str, VersionGroup]) -> set[str]:
      """Collect packages to be excluded from the rendered output.

      :param groups: The RenderGroups to collect excluded packages from
      :return: The package keys of the packages to exclude
      """
      excluded: set[str] = set()
      for grp in groups.values():
         excluded.add(grp.key)
      return excluded

   def _render_summaries(self):
      """Collect summaries for each functional group."""
      for rgrp in self.groups:
         if not rgrp.groups:
            self._sections[rgrp.name] = ''
            continue
         lines = rgrp.render_summary(self.format, self)
         self._sections[rgrp.name] = '\n'.join(lines)

   def _render_long(self):
      """Collect long license descriptions for each package."""
      lines = []
      packages = sorted(self.packages.values(), key=lambda g: g.name.replace('@', '').upper())
      for vgrp in packages:
         if vgrp.key in self.excluded or vgrp.name not in self._included:
            continue
         lines.extend(vgrp.render_long(self.format, self))
      self._sections['component-licenses'] = '\n'.join(lines)

   def _render_licenses(self):
      """Collect text for licenses used across multiple packages."""
      section = []
      for ltype, path in sorted(self.shared_licenses.items()):
         template = populate_template(
            self.format,
            'shared_license',
            {
               'name': LICENSE_NAMES[ltype],
               'ltype': ltype,
               'text': self.render_license(path),
            },
         )
         section.append(template)
      self._sections['shared-licenses'] = '\n'.join(section)

   def _collect_licenses(self, pkg: RenderPackage):
      """Analyzes the license usage in a package for later collation.

      :param pkg: The package being analyzed
      """
      path_count: dict[str, int] = {}
      for path in pkg.licenses.values():
         path_count[path] = path_count.get(path, 0) + 1
      for ltype, path in pkg.licenses.items():
         info = analyze_license_file(path, ignore_uncertain=True)
         if pkg.unversioned not in self.excluded and info['clean']:
            compare_ltype = normalize_ltype_for_comparison(ltype)
            if compare_ltype not in self.license_usage:
               self.license_usage[compare_ltype] = set()
            self.license_usage[compare_ltype].add(pkg.render_name)
         if path_count[path] == 1:
            license_registry.add(ltype, info, pkg.key)

   def write(self, path: str):
      """Render the notice document to disk.

      :param path: The destination path
      """
      logger.info('Rendering %s to %s...', self._output['template'], path)
      self._render_summaries()
      self._render_long()
      self._render_licenses()
      with open(self._output['template'], 'r', encoding='utf8') as f:
         template = f.read()
      if self.markdown:
         template = auto_hyperlink(template % self._sections)
      else:
         template = strip_markdown(template % self._sections)
         template = template.replace('&lt;', '<').replace('&gt;', '>')
         # TODO: word wrap  - textwrap lib doesn't automatically detect
         # hanging indents or paragraph boundaries.
         # Out of scope for initial release.
      with open(path, 'w', encoding='utf8') as f:
         f.write(template)
