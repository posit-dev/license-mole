# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for handling Markdown text.

Copyright (c) 2025 Posit Software, PBC
"""

import re
from dataclasses import dataclass
from typing import Literal, Union

LINK_PATTERN = re.compile(r'[\[]([^\]]+)[\]]\([^\)]+\)')
BRACKET_ENTITIES = re.compile(r'<([^>]*)>')
WHITESPACE = re.compile(r'\s')
BOLD_TAG = re.compile(r'(?<![*])[*]\s*(.+?)\s*[*](?![*])')
BLOCKQUOTE_PREFIX = re.compile(r'^\s*([>#]\s*)*', re.M)
TRIPLE_QUOTE_PREFIX = re.compile(r'^(\s*)"""')
UNLINKED_HYPERLINK = re.compile(r'(?<!.\[|]\()(https?://(?:[-A-Za-z0-9#.:/?=~@+%]|&(?!gt;))+)')
URL_MISSING_SLASHES = re.compile(r'http(s?):([A-Za-z])')
NUMERIC_LIST_PREFIX = re.compile(r'^\s*(\(?\d+\)|\d+[.])(?=\s)')
ALPHA_LIST_PREFIX = re.compile(r'^\s*(\(?[a-z]\)|[a-z][.])(?=\s)')
ROMAN_LIST_PREFIX = re.compile(r'^\s*(\(?[ivx]+\)|[ivx]+[.])(?=\s)')
BULLET_LIST_PREFIX = re.compile(r'^\s*([-*])(?=\s)')
LIST_PREFIXES = [ALPHA_LIST_PREFIX, NUMERIC_LIST_PREFIX, ROMAN_LIST_PREFIX, BULLET_LIST_PREFIX]
LIST_DEDENT_PREFIX = re.compile(r'^((?:> )*) {4,}')
SINGLE_LINE = re.compile(r'^[\s>#*]*[-*]{4,}[\s*]*$')
DOUBLE_LINE = re.compile(r'^[\s>#*]*====+[\s*]*$')
CC_BY_40_SPECIAL = ['a. reproduce', 'b. produce', 'a. Offer', 'b. No downstream']
GPL_SPECIAL = ['0) Convey', '1) Use a']
GPL_SPECIAL_2 = 'one line to give'
GPL_SPECIAL_3 = re.compile(r"`show (.)'")
MPL_SPECIAL = re.compile(r'\d+[.]\d+[.]\s+"')
LIST_MISTAKE_SPECIAL = re.compile(r'(\([i2]\)|7\.) +(the power|offer you|This requirement)')
PYTHON_SPECIAL_START = re.compile(r'Release\s+Derived')
PYTHON_SPECIAL_END = re.compile(r'2\.2 and above\s+2\.1\.1')
BSD_SPECIAL = re.compile(r'^[>\s]*[.*] (?:Redistributions|The name)')
BSD_TERMINATOR = re.compile(r'THIS SOFTWARE (?:IS|AND DOCUMENTATION ARE) PROVIDED')
ARTISTIC_TERMINATOR = 'Distribution of Compiled Forms'
SHORT_LINE = 60
VERY_SHORT_LINE = 40
HANGING_WORD = 8


def _first_match(pattern: Union[re.Pattern, str], subject: str) -> str:
   """Return the first regex match, or an empty string if the match failed.

   :param pattern: The regexp to evaluate
   :param subject: The string to search
   :return: The first match
   """
   if isinstance(pattern, str):
      match = re.match(pattern, subject)
   else:
      match = pattern.match(subject)
   if match:
      return match[0]
   return ''


def md_link(text: str, url: str) -> str:
   """Render a Markdown link.

   If the provided URL is empty, just returns plain text.

   :param text: The text of the link
   :param url: The target of the link
   :return: Markdown text
   """
   if url:
      return f'[{text}]({url})'
   return text


def auto_hyperlink(text: str) -> str:
   """Find hyperlinks and wraps them in Markdown.

   Also corrects http:foo and https:foo to http://foo and https://foo.

   :param text: The body of text to search for hyperlinks
   :return: Markdown text
   """
   text = URL_MISSING_SLASHES.sub(r'http\1://\2', text)
   return UNLINKED_HYPERLINK.sub(r'[\1](\1)', text)


def strip_markdown(text: str) -> str:
   """Remove Markdown formatting from a block of text.

   :param text: Markdown text to strip
   :return: Plain text
   """
   text = LINK_PATTERN.sub('\\1', text)
   text = re.sub(r'^(> )+', lambda m: ' ' * len(m[0]), text, flags=re.M)
   text = re.sub(r'^>$', '', text, flags=re.M)
   return text


@dataclass
class _ListLevel:
   list_type: str
   value: str
   indent: int


class MarkdownFixer:
   """A class to accumulate Markdown text line-by-line.

   This class generates Quarto-compatible Markdown, so it translates
   formatting found in plaintext and other Markdown variations into
   Quarto's dialect. It also fixes some special cases in known text
   files that cause Quarto to misrender the layout.

   :param replace_underlines: If True, convert underlines to headers
   :param blockquote: If True, put the entire document in a blockquote
   :param expect_blocks: If True, treat triple-quoted text as blockquotes
   :param expect_comments: If True, treat /* */ as code comments
   """

   def __init__(self,
      replace_underlines: bool = True,
      blockquote: bool = True,
      expect_blocks: bool = False,
      expect_comments: bool = False,
   ):
      self._lines: list[str] = []
      self._should_replace_underlines = replace_underlines
      self._blockquote = int(blockquote)
      self._expect_blocks = expect_blocks
      self._expect_comments = expect_comments
      self._in_comment = False
      self._in_line_comment = False
      self._list_stack: list[_ListLevel] = []
      self._triquote_depth = 0
      self._first_triquote_depth = 0
      self._indent = ''
      self._hash_block = False
      self.set_quote_level(self._blockquote)

   def render(self) -> str:
      """Render the collected Markdown with duplicated lines removed.

      :return: Markdown text
      """
      # Remove leading/trailing blank lines
      while self._lines and not self._lines[0].replace('>', '').strip():
         del self._lines[0]
      while self._lines and not self._lines[-1].replace('>', '').strip():
         self._lines.pop()
      # Remove duplicated lines
      return '\n'.join(line for i, line in enumerate(self._lines) if i == 0 or self._lines[i - 1] != line)

   def set_quote_level(self, amount: int):
      """Set the current blockquote level.

      :param amount: The number of blockquote levels
      """
      self._quote_level = amount
      list_indent = sum(l.indent for l in self._list_stack)
      self._indent = '> ' * self._quote_level + ' ' * list_indent

   def push_list(self, list_type: str, value: str, indent: int):
      """Increases the current outline nesting depth.

      :param list_type: 'A', '1', or 'i' to indicate list type
      :param value: The first index in the list
      :param indent: Hanging indent size, in characters
      """
      self._list_stack.append(_ListLevel(list_type, value, indent))
      self.set_quote_level(self._quote_level)

   def pop_list(self):
      """Decreases the current outline nesting depth."""
      self._list_stack.pop()
      self.set_quote_level(self._quote_level)

   def clear_list(self):
      """Immediately closes all open outlines."""
      self._list_stack.clear()
      self.set_quote_level(self._quote_level)

   @property
   def _list_type(self) -> str:
      if not self._list_stack:
         return ''
      return self._list_stack[-1].list_type

   def _quote_boundary(self, line: str):
      """Handle a triple-quoted block start/end.

      Precondition: A triple quote MUST exist in the input string.

      :param line: A line containing a triple-quote
      """
      new_triquote_depth = len(_first_match(TRIPLE_QUOTE_PREFIX, line))
      if new_triquote_depth > self._triquote_depth:
         if self._triquote_depth == 0:
            self._first_triquote_depth = new_triquote_depth
         # If adding a new indent level make sure there's a blank line
         self._add_line(False)
         self.set_quote_level(self._quote_level + 1)
      else:
         if new_triquote_depth <= self._first_triquote_depth:
            new_triquote_depth = 0
         self.set_quote_level(self._quote_level - 1)
      self._triquote_depth = new_triquote_depth
      self.clear_list()

   def _update_quote_level(self, line: str) -> None:
      """Update the blockquote level based on the prefix of the next line.

      :param line: The next line being processed
      """
      if self._triquote_depth:
         return
      new_level = len(re.sub(r'\s', '', _first_match(r'^\s*(>\s*)*', line))) + self._blockquote
      if new_level != self._quote_level:
         if new_level > self._quote_level and len(self._lines) > 0:
            # If adding a new quote level make sure there's a blank line
            self._add_line(False)
         # kill any running lists when changing quote levels
         self.clear_list()
         self.set_quote_level(new_level)

   def _is_list_terminator(self, line: str) -> bool:
      """Check if a line is a list terminator.

      A list terminator is a single short line with blank lines on both sides,
      or a large heading, or (as a special case) the final clause of BSD
      licenses.

      :param line: The line being processed
      :return: True if the line doesn't belong to the list
      """
      if '##' in line or BSD_TERMINATOR.search(line) or ARTISTIC_TERMINATOR in line:
         # Heading or BSD/Artistic license clause
         return True
      if len(self._lines) <= 1 or line.strip():
         # If we're not in a list or the current line isn't blank, this isn't a terminator
         return False
      if self._lines[-2].replace('>', '').strip():
         # A terminator must be preceded by a blank line
         return False
      prev = self._lines[-1].replace('>', '').strip()
      if not prev or any(prefix.match(prev) for prefix in LIST_PREFIXES):
         # A blank line or a list entry is not a terminator
         return False
      # Long single lines may still be part of the list
      return bool(len(prev) <= SHORT_LINE or SINGLE_LINE.match(prev) or DOUBLE_LINE.match(prev))

   def _update_list(self, line: str) -> bool:
      """Check for numbered lists and updates indentation if needed.

      :param line: The next line being processed
      :return: True if this is the first line of a list entry
      """
      if match := NUMERIC_LIST_PREFIX.match(line):
         list_type = '1'
      elif match := ROMAN_LIST_PREFIX.match(line):
         list_type = 'i'
      elif match := ALPHA_LIST_PREFIX.match(line):
         list_type = 'A'
      elif match := BULLET_LIST_PREFIX.match(line):
         list_type = match[1]
      else:
         if self._list_stack and self._is_list_terminator(line):
            # end the list and correct the indentation of the terminator
            self._lines[-1] = LIST_DEDENT_PREFIX.sub(r'\1', self._lines[-1])
            self.clear_list()
         return False
      value = match[1]
      if value == 'i' and self._list_stack:
         # i could be a Roman numeral or a letter
         if self._list_stack[-1].value == 'h':
            list_type = 'A'
      # Find counter type in stack
      pop_to = -1
      for i, stack in enumerate(self._list_stack):
         if stack.list_type == list_type:
            pop_to = i
            break
      if pop_to < 0:
         # New counter type
         self.push_list(list_type, value, len(match[0].strip()) + 1)
         return True
      while len(self._list_stack) - 1 > pop_to:
         self.pop_list()
      self._list_stack[-1].value = value
      return True

   def _try_open_comment(self, line: str) -> None:
      """Check for the start of a comment block.

      :param line: The next line being processed
      """
      if '// ' in line + ' ':
         self._in_comment = True
         self._in_line_comment = True
      elif self._in_line_comment:
         self._in_comment = False
         self._in_line_comment = False
      if not self._expect_comments or self._in_comment:
         return
      if '/*' in line:
         line_indent = _first_match(BLOCKQUOTE_PREFIX, line)
         self._add_line(line_indent.rstrip() + ' ```')
         self._in_comment = True

   def _try_close_comment(self, line: str):
      """Check for the end of a comment block.

      :param line: The next line being processed
      """
      if self._expect_comments and self._in_comment and '*/' in line:
         self._in_comment = False
         line_indent = _first_match(BLOCKQUOTE_PREFIX, line)
         self._add_line(line_indent.rstrip() + ' ```')

   def _format_special_cases(self, line: str) -> str:  # noqa: PLR0911,PLR0912
      """Apply special-case fixes.

      Some licenses are misformatted when rendered in Quarto. To try to keep
      the main rendering code clean, the special cases are collected here.

      This function is called before blockquotes are applied. Any leading >
      symbols will be found in the `indent` parameter.

      :param line: The new line to be rendered
      :return: The fixed line
      """
      # If the line starts with a copyright notice, make sure there's a line break
      if line.startswith('Copyright'):
         self._add_line(False)
         return line
      # Don't misrender CC-BY-4.0 2(a)(1)
      if any(prefix in line for prefix in CC_BY_40_SPECIAL):
         return line.replace('a. ', 'i. ').replace('b. ', 'ii. ')
      # Don't misrender GPL 4(d)
      if any(prefix in line for prefix in GPL_SPECIAL):
         return line.replace('0) ', 'i) ').replace('1) ', 'ii) ')
      # Don't misrender GPL example texts or MPL clause 1.6
      if GPL_SPECIAL_2 in line or MPL_SPECIAL.search(line):
         self.clear_list()
         return line.strip()
      if GPL_SPECIAL_3.search(line):
         return GPL_SPECIAL_3.sub(r'`show \1`', line)
      # Handle BSD licenses without blank lines
      if BSD_SPECIAL.search(line):
         # We can add a blank line unconditionally because it will be removed later
         self._add_line(False)
         return line
      # Don't misrender version table in Python license
      if PYTHON_SPECIAL_START.search(line):
         self._add_line(self._indent + '```')
         self._in_comment = True
         return '    ' + line
      if PYTHON_SPECIAL_END.search(line):
         self._in_comment = False
         return f'{line}\n{self._indent}```'
      # The remaining special cases require at least one line of context
      if len(self._lines) == 0:
         return line
      prev = self._lines[-1]
      # Don't misrender CC-BY-4.0 2(a)(4)
      if line.startswith('(4)') and prev.endswith('2(a)'):
         self._lines[-1] += '(4)'
         return line[3:].strip()
      # Fix linewrapping that looks like a list item
      if match := LIST_MISTAKE_SPECIAL.match(line):
         self._lines[-1] += ' ' + match[1]
         return line.replace(match[0], match[2])
      # If the previous line was very short, assume it was meant to be separate lines
      if len(prev) < VERY_SHORT_LINE and len(line) > HANGING_WORD:
         self._add_line(False)
         return line
      return line

   def _convert_underlines(self, line: str) -> bool:
      """Convert underline-based headers to #-based headers.

      :param line: The line being processed
      :return: True if this was an underline or separator
      """
      if not self._lines or not self._should_replace_underlines:
         return False
      single = SINGLE_LINE.match(line)
      double = DOUBLE_LINE.match(line)
      if not single and not double:
         return False
      prev = self._lines[-1]
      prefix = _first_match(BLOCKQUOTE_PREFIX, prev)
      # Special case: replace horizontal lines with blank lines in hash blocks
      if self._hash_block:
         self._add_line(False)
         return True
      if prev.replace(prefix, '').strip():
         level = 2 if single else 1
         level = min(4, level + len(prefix) - len(prefix.replace('>', '')))
         heading = f' {"#" * level} '
         self._lines[-1] = prev.replace(prefix, prefix.rstrip() + heading)
         return True
      # It's a separator, make sure there's a blank line after it
      # Duplicate blank lines will get cleaned up later
      self._add_line(self._indent + '---')
      self._add_line(False)
      return True

   def _apply_indent(self, line: str) -> str:
      """Apply the current indent settings to a line.

      :param line: The line being processed
      :return: The indented line
      """
      if self._in_line_comment:
         return self._indent.rstrip() + ' ' + line.strip()
      if self._in_comment:
         return self._indent + line.rstrip()
      if self._update_list(line):
         line = line.strip()
         if line.startswith('('):
            line = line[1:]
         return self._indent[:-self._list_stack[-1].indent] + line
      return self._indent + line.strip()

   def _add_line(self, line: Union[str, Literal[False]]):
      """Append a line (internal worker function).

      :param line: The line to append, or False to add a blank line
      """
      if line is False:
         self._lines.append(self._indent.rstrip())
      else:
         self._lines.append(line.rstrip())

   def append(self, line: str) -> None:
      """Add a line to the document.

      :param line: The line to append
      """
      if not line.strip():
         # Preserve the current indentation if the line is blank and we're in a block
         # self._in_line_comment = False
         self._update_list(line)
         self._add_line(False)
         return
      if self._expect_blocks and line.strip() == '"""':
         self._quote_boundary(line)
         return
      self._update_quote_level(line)
      if self._convert_underlines(line):
         return

      self._try_open_comment(self._indent + line)

      if not self._in_comment:
         # Some licenses (Node.js) use ` # ` as a blockquote. Translate it to a blockquote.
         # No space before the # means it's a heading instead.
         if match := re.match(r'^\s+#', line):
            if not self._hash_block:
               self._hash_block = True
               self.set_quote_level(self._quote_level + 1)
            line = line.replace(match[0], '')
         elif self._hash_block:
            self._hash_block = False
            self.set_quote_level(self._quote_level - 1)
         line = re.sub(r'^\s+#', r'| ', line)
         # Translate bold markers between Markdown dialects
         line = BOLD_TAG.sub(r'**\1**', line)
         # If the line starts with a word character, a line divider, a bullet, a quote,
         # or a parenthesis, normalize the leading whitespace
         line = re.sub(r'^((?:>\s)*)\s+(\w|--+|==+|\*|"|[()])', r'\1\2', line)
         # Reduce heading scopes within blockquotes
         if self._blockquote and line.startswith('#'):
            line = '#' + line
         # Fix <> entities and special cases
         line = BRACKET_ENTITIES.sub(r'&lt;\1&gt;', self._format_special_cases(line))
         # Clean out unnecessary formatting noise
         if not line.replace('#', '').replace('*', '').strip():
            line = ''
      else:
         # In a comment, treat a ` # ` blockquote as spacing.
         line = re.sub(r'^\s+#', r' ', line)

      line = self._apply_indent(line)

      self._add_line(line)
      self._try_close_comment(line)
