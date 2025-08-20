# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for heuristically parsing license files.

Copyright (c) 2025 Posit Software, PBC

By convention, the name `ltype` is used to refer to an SPDX-style license
identifier across the codebase.
"""

import glob
import hashlib
import os
import re
import zipfile
from typing import Optional, TypedDict, Union

from .. import logger, markdown
from ..cache import download_file_cached
from ..config import get_file_overrides
from ..repo import find_file_in_repo
from . import resources

# from .override import get_file_overrides

# Clauses that indicate the end of a copyright attribution
SPLIT_CLAUSES = [
   'Permission is hereby granted',
   'All rights reserved',
   'All Rights Reserved',
   'Copyright and related rights for',
   'Everyone is permitted to copy',
   'Redistribution and use',
   'The above copyright notice',
   'THE SOFTWARE IS PROVIDED',
   'Based on ',
   'Derived from ',
   'This package is an SSL implementation',
   'Permission to use',
   'Distributed under',
   '-----',
   '=====',
]
# Simplifications to make it easier to identify copyright attribution
# and correlate license files together
CLEAN_REPLACEMENTS = [
   (re.compile(r'\*'), ''),
   (re.compile(r'#'), ''),
   (re.compile(r'^[/\s-]+'), ''),
   (re.compile(r'\s$'), ''),
   (re.compile(r' \d[.] '), ' '),
   (re.compile(r'\(i+\)'), ''),
   (re.compile(r'\([abc]\)'), ''),
   (re.compile(r'\(?(?:The )?MIT(?:/X11)? License\)?', re.I), ''),
   (re.compile(r'\(MIT\)'), ''),
   (re.compile(r'\(?(?:The )?BSD (?:[23]-Clause )?License\)?'), ''),
   (re.compile(r'All rights reserved\.?'), ''),
   (re.compile(r'[/]{2,}'), ''),
   (markdown.LINK_PATTERN, '\\1'),  # clean up Markdown links
   (re.compile(r'copyright .?yyyy.? .?name of copyright owner.?', re.I), ''),  # remove false positive from Apache
   (re.compile(r'This software is released under', re.I), ''),
   (re.compile(r'Copyright\('), 'Copyright ('),
   (re.compile(r' \.'), '.'),
]
# Identifies lines that look like copyright attribution but aren't
FALSE_POSITIVES = [
   # Apache license includes example text
   '[name of copyright owner]',
   '{name of copyright owner}',
   # GPL/AGPL text is copyright FSF but doesn't apply to packages
   'Copyright (C) 2007 Free Software Foundation, Inc',
   'Copyright (C) 1989, 1991 Free Software Foundation, Inc',
   # CC0 text has a line that coincidentally matches patterns
   'Copyright and Related Rights.',
   # Looks like a copyright attributed to someone named "notice"
   'Copyright notice:',
   # Something about this line in GPLv2 gets detected as attribution
   'If you wish to incorporate parts',
]
# Attribution introductions
ATTRIBUTION_SPLIT = re.compile(r'(?=Copyright)')
# Replace all whitespace with a single space
SIMPLIFY_WHITESPACE = re.compile(r'\s+', re.M)
# Used to identify if a copyright line needs an additional line for attribution
COPYRIGHT_CHECK = re.compile(r'Copyright|\(c\)|\xa9|&copy;|\d+||\s', re.I)
# Used to tell if we need to insert "Copyright" at the beginning
COPYRIGHT_PREFIX = re.compile(r'^\(c\)|^\xa9|^&copy;', re.I)
# Easy identification markers
# These are used as a last resort to avoid misattributing files that merely reference a license
# Only include strings that are completely unambiguous!
# In particular, "LICENSE.BSD" was intentionally omitted.
LICENSE_IDENTIFIERS = {
   # Many license files include the name of the license at the top
   'BSD 2-Clause License': 'BSD-2-Clause',
   'BSD 3-Clause License': 'BSD-3-Clause',
   'Apache License Version 2': 'Apache-2.0',
   'Boost Software License - Version 1.0 - August 17th, 2003': 'BSL-1.0',
   'MIT License': 'MIT',
   'The ISC License': 'ISC',
   'Mozilla Public License Version 1.1': 'MPL-1.1',
   'Mozilla Public License Version 2.0': 'MPL-2.0',
   'GNU AFFERO GENERAL PUBLIC LICENSE Version 3': 'AGPL-3.0',
   'GNU GENERAL PUBLIC LICENSE Version 3': 'GPL-3.0',
   'GNU GENERAL PUBLIC LICENSE Version 2': 'GPL-2.0',
   'GNU LESSER GENERAL PUBLIC LICENSE Version 2.1': 'LGPL-2.1',
   'Academic Free License version 2.1': 'AFL-2.1',
   'Creative Commons Attribution 4.0': 'CC-BY-4.0',
   'CC0 1.0 Universal': 'CC0-1.0',
   'Creative Commons Zero': 'CC0-1.0',
   'Boost Software License': 'BSL-1.0',
   'Elastic License 2.0': 'Elastic-2.0',
   'Jean-loup Gailly and Mark Adler': 'zlib',
   'either version 2.1 of the License': 'LGPL-2.1-or-later',
   'LLVM Exceptions to the Apache 2.0 License': 'Apache-2.0-WITH-LLVM-Exceptions',
   # BSD and MIT frequently don't include a title but have identifiable clauses
   'to endorse or promote products derived': 'BSD-3-Clause',
   'The above copyright notice and this permission notice shall be included': 'MIT',
   # BSD-3-Clause is sometimes rephrased to be generic, but the generic
   # rephrasings aren't standardized, and I don't trust "Neither the name of"
   # to be sufficient to uniquely identify BSD-3-Clause.
   'Neither the name of Google': 'BSD-3-Clause',
   # SQLite has a public-domain blessing
   'here is a blessing': 'SQLite-Blessing',
   # References to Creative Commons licenses are usually not in SPDX format
   'CC BY 3.0': 'CC-BY-3.0',
   'CC BY 4.0': 'CC-BY-4.0',
   # Filename extensions
   '.APACHE2': 'Apache-2.0',
   '.MIT': 'MIT',
   'LICENSE-ISC': 'ISC',
   'LICENSE-MIT': 'MIT',
   'LICENSE-APACHE': 'Apache-2.0',
   'LICENSE-Apache-2.0_WITH_LLVM-exception': 'Apache-2.0-WITH-LLVM-Exceptions',
}
# Last-ditch effort for finding attribution
ATTRIBUTION_PATTERN = re.compile('(?:Copyright|\\([cC]\\)|\xa9|&copy;)\n?.*(?:$|\n)')  # noqa: RUF039
# Specific filenames to check when scraping a website for readmes
ATTRIBUTION_FILENAMES = [
   '/README',
   '/AUTHORS',
   '/README.md',
]

NON_ALPHA = re.compile(r'[^A-Za-z]')
MULTI_NEWLINE = re.compile('\n{2,}')  # noqa: RUF039


class LicenseInfo(TypedDict):
   """Heuristic description of a license file.

   :ivar author: The author passed into this function
   :ivar path: The path passed into this function
   :ivar attribution: Detected copyright attribution lines
   :ivar spdx: Unambiguously-detected SPDX identifiers
   :ivar guess: Heuristically-inferred SPDX identifier, if any
   :ivar checksum: The checksum of the normalized license text
   :ivar multi: File has multiple detected licenses inside
   :ivar clean: File can be reused for other packages
   """

   author: Optional[str]
   path: str
   attribution: list[str]
   spdx: tuple[str, ...]
   guess: Optional[str]
   checksum: str
   multi: bool
   clean: bool


# A cache to speed up analysis of already-examined files
ANALYZE_CACHE: dict[str, LicenseInfo] = {}


def normalize_license_code(ltype: str) -> tuple[str, ...]:
   """Split a license identifier into a tuple of SPDX identifiers.

   The result is suitable for rendering, but not for comparison.
   See `licenses.normalize_ltype_for_comparison` for a normalization scheme
   that will allow license identifiers to be compared to each other.

   :param ltype: Non-normalized license identifier
   :return: A tuple of license identifiers
   """
   if '://' in ltype:
      info = analyze_license_file(ltype, ignore_uncertain=True)
      if info['spdx']:
         return info['spdx']
      if info['guess']:
         return (info['guess'],)
      return ()

   ltype = (ltype
      .replace('(', '')
      .replace(')', '')
      .replace(' OR ', '/')
      .replace(' or ', '/')
      .replace(' AND ', '/')
      .replace(' and ', '/')
      .replace('v2', '-2')
      .replace('V2', '-2')
      .replace('-2+', '-2.0-OR-LATER')
      .replace('-2.1+', '-2.1-OR-LATER')
      .replace('-3+', '-3.0-OR-LATER')
   )
   if ltype.upper().endswith('LLVM-EXCEPTION'):
      ltype += 's' if ltype[-1] == 'n' else 'S'
   if not ltype:
      return ()
   if '/' in ltype and ltype.upper() != 'MIT/X11':
      ltypes = tuple(ltype.split('/'))
   else:
      ltypes = (ltype,)
   return tuple(t.strip('- ') for t in ltypes)


def _clean_copyright_line(line: str) -> Optional[list[str]]:
   """Attempt to remove irrelevant text from a copyright attribution line.

   If no text remains after irrelevant strings are removed, this function
   returns None.

   If multiple attributions are included in the attribution line, they are
   separated into a list.

   :param line: An attribution line
   :return: A list of attribution lines
   """
   if any((msg in line) for msg in FALSE_POSITIVES):
      return None

   for pat, rep in CLEAN_REPLACEMENTS:
      line = pat.sub(rep, line)

   if COPYRIGHT_PREFIX.search(line):
      line = 'Copyright ' + line

   if not line.startswith('Copyright ') and 'is copyright' not in line:
      return None

   for clause in SPLIT_CLAUSES:
      pos = line.find(clause)
      if pos >= 0:
         line = line[:pos].strip()

   if 'Copyright' not in line:
      line = SIMPLIFY_WHITESPACE.sub(' ', line).strip()
      return [line] if line else []

   lines = []
   for l in ATTRIBUTION_SPLIT.split(line):
      l = SIMPLIFY_WHITESPACE.sub(' ', l).strip()

      # check for false positives again after cleanup
      if any((msg in l) for msg in FALSE_POSITIVES):
         continue

      if l and l.upper() != 'COPYRIGHT':
         # Don't count lines that just end up as the single word "copyright"
         lines.append(l)

   return lines


def _guess_identifier(clean_license: str, only_one: bool = False) -> tuple[str, ...]:
   """Guesses the SPDX identifier for a body of license text or a filename.

   For a filename, the results may be considered reliable. For license text,
   it's usually right but it should be considered a method of last resort.

   If a file contains signals for more than one license, this function treats
   it as ambiguous (perhaps the file contains multiple licenses) and returns
   an empty string.

   :param clean_license: License text, as cleaned by `analyze_license_text`
   :param only_one: If True, return a single type or nothing at all
   :return: Detected license identifier, if found
   """
   if clean_license.startswith('spdx://'):
      return normalize_license_code(clean_license.replace('spdx://', ''))
   clean_license = clean_license.upper()
   ltypes: set[str] = set()
   for test, ltype in LICENSE_IDENTIFIERS.items():
      if test.upper() in clean_license:
         for other in list(ltypes):
            # Handle variations
            if other in ltype:
               ltypes.remove(other)
            elif ltype in other:
               ltype = other
         ltypes.add(ltype)
   if only_one and len(ltypes) != 1:
      return ()
   return tuple(ltypes)


def get_license_text(path: str) -> str:
   """Fetch the text of a license from a path/URL.

   Newlines are normalized. Input is expected to be in UTF-8 format.

   License paths support a special anchor format for extracting a license from a
   larger text file based on text markers contained in the file. (It is not
   recommended to use this on HTML files, and HTML anchors are not supported.)

      <url-or-path>#start        License text starts after the string "start"

      <url-or-path>#start#end    License text is between "start" and "end"

   :param path: URL or path to license file
   :return: The text of the license file
   """
   if path.startswith('spdx://'):
      return resources.get_standard_license_text(path)
   anchor = None
   end_anchor = None
   if '#' in path:
      path, anchor, end_anchor = [*path.split('#'), ''][:3]

   if path.startswith('http') and '://' in path:
      text = download_file_cached(path)
   elif '.jar:' in path:
      jarpath, filepath = path.split('.jar:')
      with zipfile.ZipFile(jarpath + '.jar') as jar:
         with jar.open(filepath, 'r') as f:
            text = f.read().decode()
   else:
      with open(path, 'r', encoding='utf8') as f:
         text = f.read()

   if anchor is not None:
      text = text.split(anchor, maxsplit=1)[1]
      if end_anchor:
         text = text.split(end_anchor, maxsplit=1)[0]

   text = text.replace('\r\n', '\n')
   text = text.replace('\nCopyright', '\n\nCopyright')
   text = MULTI_NEWLINE.sub('\n\n', text)
   return text


def _find_readme_files(path: str) -> list[str]:
   """Look for readme files in a directory.

   A file is considered a readme file if it contains (case-insensitive) the
   word "README".

   This function is only used to try to collect copyright attribution if it
   could not be found in the license files.

   :param path: Directory to search
   :return: List of detected readme files
   """
   result = []
   if path.startswith('http://') or path.startswith('https://'):
      for fn in ATTRIBUTION_FILENAMES:
         url = find_file_in_repo(path, fn)
         if url:
            result.append(url)
      return result
   for fn in glob.glob(os.path.join(path, '*')):
      testfn = os.path.basename(fn).upper()
      if 'README' in testfn:
         result.append(fn)
   return [fn for fn in result if os.path.exists(fn)]


def get_readme_attribution(path: str) -> list[str]:
   """Extract attribution lines from a readme file.

   :param path: Path to readme file
   :return: List of copyright attribution lines
   """
   for fn in _find_readme_files(path):
      if fn.startswith('http://') or fn.startswith('https://'):
         text = download_file_cached(fn)
      else:
         with open(fn, 'r', encoding='utf8') as f:
            text = f.read()
      attrib = []
      for l in ATTRIBUTION_PATTERN.findall(text):
         l = SIMPLIFY_WHITESPACE.sub(' ', l)
         attrib.extend(_clean_copyright_line(l) or [])
      if attrib:
         return attrib
   return []


def _get_license_file_override(path: str) -> Union[bool, tuple[str, ...]]:
   """Check for explicit file overrides for the specified path.

   :param path: Path to license file
   :return: SPDX identifer tuple
   """
   return get_file_overrides(path) or False


def _extract_attribution(license_info: LicenseInfo, lines: list[str], ignore_uncertain: bool):
   """Extract attribution lines from license text.

   :param license_info: The license info dict to accumulate the results into
   :param lines: The lines of license text to analyze
   :param ignore_uncertain: If True, suppress logging warnings
   """
   override = _get_license_file_override(license_info['path'])
   combine_with_next = None
   for line in lines:
      if not override and 'SPDX-License-Identifier:' in line:
         spdx_id = SIMPLIFY_WHITESPACE.sub(' ', line.split('SPDX-License-Identifier:')[1]).strip('/*|- ')
         license_info['spdx'] = normalize_license_code(spdx_id)
         continue

      if combine_with_next:
         line = f'{combine_with_next} {line}'
         combine_with_next = None
      clean_lines = _clean_copyright_line(line)
      if clean_lines and not COPYRIGHT_CHECK.sub('', clean_lines[-1]):
         combine_with_next = clean_lines[-1]
         clean_lines = clean_lines[:-1]
      if clean_lines:
         license_info['attribution'] += clean_lines

   if combine_with_next:
      if license_info['author']:
         license_info['attribution'].append(f'{combine_with_next} {license_info["author"]}')
      else:
         if not ignore_uncertain:
            logger.warning('Uncertain copyright parsing in %s', license_info['path'])
         license_info['attribution'].append(combine_with_next)


def analyze_license_file(path: str, author: Optional[str] = '', ignore_uncertain: bool = False) -> LicenseInfo:
   """Load and analyzes a license file to collect heuristics.

   :param path: URL or path to license file
   :param author: Author from package metadata, if known
   :param ignore_uncertain: If True, suppresses warnings about uncertain attribution
   :raises ValueError: if the file contains no license text
   :return: License file description
   """
   if path in ANALYZE_CACHE:
      return ANALYZE_CACHE[path]

   license_info: LicenseInfo = {
      'author': author,
      'path': path,
      'attribution': [],
      'spdx': _guess_identifier(path, only_one=True),
      'guess': '',
      'multi': False,
      'clean': True,
      'checksum': '',
   }
   override = _get_license_file_override(path)
   if isinstance(override, tuple):
      license_info['spdx'] = override

   text = get_license_text(path)
   if not text:
      raise ValueError(f'Analyzing empty license text in {path}')

   # Separator lines usually indicate package-specific information
   license_info['clean'] = '-----' not in text

   _extract_attribution(license_info, text.split('\n\n'), ignore_uncertain)

   clean_license = SIMPLIFY_WHITESPACE.sub(' ', text).strip()
   guess = license_info['spdx'] or _guess_identifier(clean_license)
   license_info['multi'] = len(guess) > 1
   if len(guess) == 1:
      license_info['guess'] = guess[0]

   for pat, rep in CLEAN_REPLACEMENTS:
      clean_license = pat.sub(rep, clean_license)
   clean_license = NON_ALPHA.sub('', clean_license).upper()
   for attr in license_info['attribution']:
      attr = NON_ALPHA.sub('', attr).upper()
      clean_license = clean_license.replace(attr, '')

   license_info['checksum'] = hashlib.sha256(clean_license.upper().encode(), usedforsecurity=False).hexdigest()
   license_info['clean'] = license_info['clean'] and not license_info['attribution']
   license_info['attribution'] = (
      sorted(set(license_info['attribution']))
      or get_readme_attribution(os.path.dirname(path))
   )

   ANALYZE_CACHE[path] = license_info
   return license_info
