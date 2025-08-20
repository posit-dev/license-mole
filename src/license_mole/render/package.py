# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions to represent information about how components should be rendered.

Copyright (c) 2025 Posit Software, PBC
"""

import re
import zlib
from typing import Any, Optional, Union, cast

from .. import logger
from ..config import RELABEL
from ..config_format import FormatDict, UnderlineDescriptor
from ..errors import HomepageMissingError
from ..licenses import normalize_ltype_for_comparison
from ..markdown import md_link
from ..scan.package import BasePackage
from . import labels as rl
from .context import LicenseContext

CLEAN_ATTRIBUTION = [
   (re.compile(r'&lt;', re.I), '<'),
   (re.compile(r'&gt;', re.I), '>'),
   (re.compile(r'&copy;', re.I), '\xa9'),
   (re.compile(r'[\[]([^\]]+)[\]]\([^\)]+\)'), '\\1'),
   (re.compile(r'\([^)]*\)'), ' '),
   (re.compile(r'<[^>]>'), ' '),
   (re.compile(r'\s+'), ' '),
   (re.compile(r' \.'), '.'),
]
NORM_ATTRIBUTION = [
   (re.compile(r'[^A-Z]'), ''),
   (re.compile(r'PRESENT|COPYRIGHT|PACKAGEDBY|PUBLISHEDBY|DISTRIBUTEDBY'), ''),
]
ATTRIBUTION_DATES = re.compile(r'(\d{4}|present)', re.I)


def normalize_ltype(ltype: str) -> str:
   """Normalize a license type for rendering comparison.

   This does not remove variants like normalize_ltype_for_comparison does.
   It does unify "LLVM Exception" and "LLVM Exceptions".

   :param ltype: The license type
   :return: Normalized license type
   """
   ltype = ltype.replace(' ', '-').upper()
   if ltype.endswith('LLVM-EXCEPTION'):
      ltype += 'S'
   if ltype.endswith('+'):
      ltype = ltype[:-1] + '-OR-LATER'
   return ltype


def _clean_attribution(attrs: list[str]) -> list[str]:
   """Clean a set of attribution strings.

   This translates HTML entities, removes Markdown links, removes bracketed
   or parenthesized phrases (usually email addresses), and simplifies
   whitespace.

   :param attrs: A list of attribution lines
   :return: The cleaned list of attributions
   """
   result = []
   for attr in attrs:
      for pattern, rep in CLEAN_ATTRIBUTION:
         attr = pattern.sub(rep, attr)
      result.append(attr.strip())
   return result


def _version_tuple(version: str) -> tuple[int, ...]:
   parts = re.sub(r'[^\d]+', '.', version).strip('.')
   return tuple(int(p) for p in parts.split('.'))


def attribution_comparison_key(attrs: list[str]) -> tuple[str, ...]:
   """Create a comparison key for a list of attributions.

   Two packages with the same attribution comparison key have the same set of
   authors, but copyright dates may have different years.

   :param attrs: List of attributions
   :return: An attribution comparison key
   """
   result = []
   attrs = _clean_attribution(attrs)
   for attr in attrs:
      attr = attr.upper()
      for pattern, rep in NORM_ATTRIBUTION:
         attr = pattern.sub(rep, attr)
      result.append(attr)
   return tuple(sorted(set(result)))


def _attribution_dates(attr: str) -> tuple[int, ...]:
   """Parse the copyright date range from an attribution string.

   A single year is treated as being the most recent copyright, starting at
   an indeterminate time.

   The string "present" is treated as being an indeterminate time in the
   future, mostly so that this code doesn't need to check the current date.

   :param attr: An attribution line
   :return: The span of years covered by the copyright attribution
   """
   match = ATTRIBUTION_DATES.findall(attr)
   if not match:
      return ()
   years = [9999 if m.lower() == 'present' else int(m) for m in match]
   if len(years) == 1:
      return (years[0],)
   return (min(years), max(years))


def _date_range_compare(range1: tuple[int, ...], range2: tuple[int, ...]) -> bool:
   """Compare the spans of two date ranges.

   :param range1: The range being compared against
   :param range2: The range to compare
   :return: True if range1 subsumes range2
   """
   if not range1:
      return True
   if not range2:
      return False
   if len(range1) == 1:
      if len(range2) == 1:
         return range1[0] >= range2[0]
      return range2[0] <= range1[0] <= range2[1]
   if len(range2) == 1:
      return not range1[0] <= range2[0] <= range1[1]
   return range1[0] <= range2[0] and range1[1] >= range2[1]


def _format_versions(versions: list[str]) -> str:
   """Format a list of versions for rendering.

   :param versions: The list of version numbers
   :return: The formatted version list
   """
   if len(versions) > 1:
      versions = sorted(versions, key=_version_tuple, reverse=True)
      return f' versions {", ".join(versions)}'
   if len(versions) == 1:
      return f' version {versions[0]}'
   return ''


def _select_nonshared_license_files(licenses: dict[str, str], shared_licenses: dict[str, str]) -> dict[str, list[str]]:
   """Pick license files to render in a package description.

   :param licenses: The licenses for the package
   :param shared_licenses: The licenses that are shared across packages
   :return: A dictionary mapping license file paths to a list of ltypes
   """
   by_path: dict[str, list[str]] = {}
   for ltype, path in licenses.items():
      by_path[path] = [*by_path.get(path, []), normalize_ltype_for_comparison(ltype)]

   for path, ltypes in dict(by_path).items():
      if all(ltype in shared_licenses for ltype in ltypes):
         del by_path[path]

   return by_path


def _consolidate_variants(ltypes: list[str]) -> list[str]:
   """Merge license variants (e.g. with-exceptions, or-later).

   "with" variants have precedence over unlabeled.
   Unlabeled variants have precedence over "or-later".
   "only" variants have precedence over unlabeled or "or-later".

   :param ltypes: The list of license variants
   :return: The same list with variants merged
   """
   normalized = [normalize_ltype(l) for l in ltypes]
   selected: set[int] = set(range(len(ltypes)))
   for i, ltype in enumerate(ltypes):
      norm = normalize_ltype(ltype)
      if normalized.index(norm) < i:
         # duplicates in license list
         selected.discard(i)
         continue
      base = norm.split('-WITH-')[0].replace('-OR-LATER', '').replace('-ONLY', '')
      high_precedence = '-WITH-' in norm or '-ONLY' in norm
      if base != norm and base in normalized:
         other = normalized.index(base)
         if high_precedence:
            selected.discard(other)
         else:
            selected.discard(i)

   return [ltypes[i] for i in selected]


def populate_template(fmt: FormatDict, template_key: str, args: dict[str, str], underline_key: str = 'underline') -> str:
   """Interpolate args into a template, calculating an underline if necessary.

   If ``%(underline)s`` appears more than once in the template, the last one
   to appear will be used to determine the line length. This allows the use of
   an underline for box drawing.

   :param fmt: The formatting definition to be used
   :param template_key: The key into ``fmt`` containing the template
   :param args: The string interpolation arguments for the template
   :param underline_key: Which underline definition from ``fmt`` to use
   :return: Text suitable for use as an underline
   """
   template = fmt[template_key]  # type: ignore[literal-required]
   underline = cast('Optional[UnderlineDescriptor]', fmt.get(underline_key))
   if underline and underline.get('length', 0) > 0:
      args['underline'] = underline['char'] * underline['length']
   elif '%(underline)s' in template:
      preview = template.replace('%(underline)s', '{{UNDERLINE}}')
      underline_len = 0
      last_line = ''
      for line in (preview % args).split('\n'):
         if not line.strip():
            continue
         if '{{UNDERLINE}}' in line:
            padding = len(line.replace('{{UNDERLINE}}', ''))
            if len(last_line) - padding > 0:
               underline_len = len(last_line) - padding
         else:
            last_line = line
      if underline_len < 1:
         underline_len = 4
      ch = underline.get('char', '-') if underline else '-'
      args['underline'] = ch * underline_len
   return template % args


class RenderPackage:
   """A description of a package for rendering.

   This is not a BasePackage and cannot participate in dependency or license
   resolution.

   This class can collect information from a BasePackage or from a JSON cache.
   It can output a dictionary suitable for storing in a JSON cache.

   :param source: The package to render
   :param group: The functional group containing the package
   """

   def __init__(self, source: Union[BasePackage, dict[str, Any]], group: str):
      self.source = source
      self.group = group
      self.child_packages: list[RenderPackage] = []
      self.ignored = False

      if isinstance(source, dict):
         self.name = source['name']
         self.key = source['key']
         self.version = source['version']
         self.url = source['url']
         licenses = source['licenses']
         self.attribution = source['attribution']
         self.permit_license_change = source.get('permit_license_change', False)
      else:
         self.name = source.name
         self.key = source.key
         self.version = source.version
         self.permit_license_change = source.permit_license_change
         try:
            self.url = source.url
         except HomepageMissingError as e:
            self.url = f'({e})'
         licenses = {}
         for ltype in source.licenses:
            path = source.licenses.links[normalize_ltype_for_comparison(ltype)]
            licenses[ltype] = path
         self.attribution = source.licenses.attribution
         if 'PROPRIETARY' in source.licenses:
            self.ignored = True

      ltypes = _consolidate_variants(list(licenses.keys()))
      self.licenses = {ltype: licenses[ltype] for ltype in ltypes}

      self.render_name = self.name
      self.combined: Union[bool, str] = False
      for prefix, combined_name in RELABEL.items():
         if self.key.startswith(prefix):
            self.render_name = combined_name
            self.combined = prefix
            break
      self._simplify_attribution()

   def __lt__(self, other: 'RenderPackage') -> bool:
      return self.comparison_key() < other.comparison_key()

   def comparison_key(self) -> tuple[Union[str, int], ...]:
      """Produce a comparison key for sorting packages.

      The resulting sort order is:
      * Ascending by package name
      * Descending by version number

      :return: A comparison key
      """
      key: list[Union[str, int]] = [self.combined or self.unversioned]
      if self.version:
         key.extend(-p for p in _version_tuple(self.version))
      return tuple(key)

   def merge(self, other: 'RenderPackage'):
      """Combine another RenderPackage into this one.

      :param other: The package to be combined
      :raises ValueError: if the package to be merged is incompatible
      """
      if other.render_name != self.render_name:
         raise ValueError('merging incompatible packages {self.key} and {other.key}: name mismatch')
      if list(other.licenses.keys()) != list(self.licenses.keys()):
         # TODO: it would be nice if this could control directionality
         if self.permit_license_change or other.permit_license_change:
            for ltype, path in other.licenses.items():
               if ltype not in self.licenses:
                  self.licenses[ltype] = path
         else:
            raise ValueError(f'merging incompatible packages {self.key} and {other.key}: license mismatch')
      self.child_packages.append(other)
      self.attribution.extend(other.attribution)
      self._simplify_attribution()

   def _simplify_attribution(self):
      """Simplifies the attribution for the package.

      Duplicate lines are removed.
      Multiple copyright lines for the same author are combined.
      """
      attr_map: dict[str, str] = {}
      for attr in self.attribution:
         key = attribution_comparison_key([attr])[0]
         existing = attr_map.get(key)
         if not existing:
            attr_map[key] = attr
            continue
         if existing == attr:
            continue
         old_years = _attribution_dates(existing)
         new_years = _attribution_dates(attr)
         if _date_range_compare(old_years, new_years):
            # old range subsumes new range
            continue
         if _date_range_compare(new_years, old_years):
            # new range subsumes old range
            attr_map[key] = attr
            continue
         # uncertain, debug
         logger.warning('Uncertain date range comparison in %s (%s vs %s), please debug', self.key, old_years, new_years)
         attr_map[attr] = attr
      self.attribution = sorted(set(attr_map.values()))

   def to_dict(self) -> dict[str, Any]:
      """Serialize this object.

      :return: A dictionary suitable for serialization
      """
      serialized = {
         'group': self.group,
         'name': self.name,
         'key': self.key,
         'url': self.url,
         'version': self.version,
         'licenses': self.licenses,
         'attribution': self.attribution,
      }
      if self.permit_license_change:
         serialized['permit_license_change'] = True
      return serialized

   @property
   def unversioned(self) -> str:
      """The package key with version removed."""
      return self.key.split('=')[0]

   def _anchor(self) -> str:
      """Construct an anchor attribute for internal links.

      :return: An anchor attribute
      """
      anchor = self.render_name
      attr_key = ','.join(str(x) for x in sorted(self.licenses.items()))
      attr_key = hex(zlib.crc32(attr_key.encode()))[2:]
      anchor = anchor + '-' + attr_key
      anchor = re.sub(r'[^A-Za-z0-9]', '-', anchor)
      anchor = re.sub(r'--+', '-', anchor.strip('-'))
      anchor = self.key.split('::')[0] + '-' + anchor
      return anchor.lower()

   def render(self, fmt: FormatDict, show_versions: list[str]) -> str:
      """Render a one-line package summary in Markdown.

      :param fmt: Description of the rendering format
      :param show_versions: A list of version numbers to display
      :return: Markdown-formatted text
      """
      if not self.combined:
         # If you want e.g. "(npm package)" on a combined package,
         # put it in the render name
         package_type = rl.PACKAGE_TYPES.get(self.key.split('::')[0], '')
      else:
         package_type = ''
      ltypes = sorted(normalize_ltype(l) for l in self.licenses.keys() if l != 'MULTI')
      licenses = ', '.join(rl.LICENSE_SHORT_NAMES.get(normalize_ltype(l), l) for l in ltypes)
      if len(ltypes) > 1:
         licenses += ' licenses'
      elif len(ltypes) == 1:
         if normalize_ltype(ltypes[0]) not in rl.LICENSE_MESSAGES:
            licenses += ' license'
      elif len(ltypes) == 0 and 'MULTI' in self.licenses:
         logger.debug('MULTI license for %s', self.key)
         licenses = 'multiple licenses'
      return populate_template(
         fmt,
         'toc_line',
         {
            'name': self.render_name,
            'anchor': self._anchor(),
            'type': package_type,
            'licenses': licenses,
            'versions': _format_versions(show_versions),
         },
      )

   def render_long(self, fmt: FormatDict, show_versions: list[str], context: LicenseContext) -> str:
      """Render full attribution and licensing in Markdown to stdout.

      :param fmt: Description of the rendering format
      :param show_versions: A list of version numbers to display
      :param context: The context containing shared license information
      :return: A block of Markdown text
      """
      by_path = _select_nonshared_license_files(self.licenses, context.shared_licenses)

      license_messages = ''
      if len(self.licenses) == 1:
         ltype = normalize_ltype(next(iter(self.licenses.keys())))
         if ltype in rl.LICENSE_MESSAGES:
            message = rl.LICENSE_MESSAGES.get(ltype)
            if message:
               license_messages = fmt['message_line'] % {'message': message}
         elif ltype in rl.LICENSE_NAMES:
            license_messages = fmt['license_line'] % {
               'name': md_link(
                  rl.LICENSE_NAMES[ltype],
                  f'#{ltype}' if ltype in context.shared_licenses else '',
               ),
            }
      else:
         lines = []
         for ltype, path in sorted(self.licenses.items()):
            ltype = normalize_ltype(ltype)
            use_link = ltype in context.shared_licenses and path not in by_path
            lines.append(md_link(
               rl.LICENSE_NAMES[ltype],
               ltype if use_link else '',
            ))
         license_messages = fmt['multi_license_lines'] % {
            'licenses': '\n'.join(f'{fmt["multi_license_indent"]}{l}' for l in lines),
            'package': self.render_name,
         }

      license_text = []
      templates = ['nameless_license', 'named_license', 'multi_license']
      for path, ltypes in by_path.items():
         license_names = sorted(rl.LICENSE_NAMES[ltype] for ltype in ltypes if ltype in rl.LICENSE_NAMES)
         license_text.append(
            populate_template(
               fmt,
               templates[min(len(license_names), 2)],
               {
                  'name': ', '.join(license_names),
                  'names': ', '.join(license_names),
                  'text': context.render_license(path),
               },
               'license_header_underline',
            ),
         )
      return populate_template(
         fmt,
         'package',
         {
            'name': self.render_name,
            'url': self.url,
            'versions': _format_versions(show_versions),
            'anchor': self._anchor(),
            'attribution': '\n'.join((fmt['attribution_line'] % {'message': attr}) for attr in self.attribution),
            'messages': license_messages,
            'license': '\n'.join(license_text),
         },
      )
