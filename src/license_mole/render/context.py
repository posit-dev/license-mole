# vim: ts=3 sts=3 sw=3 expandtab:
"""Container for shared rendering information.

Copyright (c) 2025 Posit Software, PBC
"""

from ..config_format import FormatDict
from ..licenses.parse import get_license_text
from ..markdown import MarkdownFixer


class LicenseContext:
   """A minimal container for tracking license usage across packages."""

   license_usage: dict[str, set[str]]
   shared_licenses: dict[str, str]
   merged_anchors: dict[str, str]
   excluded: set[str]
   format: FormatDict
   markdown: bool

   def __init__(self, fmt: FormatDict) -> None:
      # maps comparison-ltype to list of packages to see which licenses are only used once
      self.license_usage = {}
      # licenses that appear in this dict have text shared across packages
      self.shared_licenses = {}
      # maps child package anchors to merged package anchors
      self.merged_anchors = {}
      # packages that should be omitted from the document
      self.excluded: set[str] = set()
      self.format = fmt
      self.markdown = self.format['markup'] == 'markdown'

   def render_license(self, path: str) -> str:
      """Render a license file as a blockquote.

      :param path: Path to the license file
      :return: Formatted Markdown text
      """
      text = get_license_text(path).strip('\n')
      md = MarkdownFixer(
         replace_underlines=self.markdown,
         blockquote=self.format['license_blockquote'],
         expect_blocks='"""' in text,
         expect_comments='/*' in text and '*/' in text,
      )
      for line in text.split('\n'):
         md.append(line)
      return md.render()
