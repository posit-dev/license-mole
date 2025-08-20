# vim: ts=3 sts=3 sw=3 expandtab:
"""Format configuration information.

Copyright (c) 2025 Posit Software, PBC
"""
# mypy: disable-error-code="literal-required"

import copy
import os
from typing import TypedDict

from .configfile import ConfigFile

OUTPUTS: dict[str, 'DocumentDict'] = {}


class UnderlineDescriptor(TypedDict, total=False):
   """Description of how text should be underlined."""

   length: int
   """If specified, the underline is rendered as this many copies of
   :py:attr:`char`. If omitted, the underline is rendered to the width of
   the previous line of text.
   """
   char: str
   """The character used to render the underline. Typically ``-`` or ``=``."""


class FormatDict(TypedDict, total=False):
   """Definitions for how to render portions of a document.

   There are two built-in format definitions: ``text`` and ``markdown``.
   """

   inherit: str
   """Specifies another format definition to inherit from.

   Any options not specified will use the value from the inherited format.

   By default, custom formats inherit from the built-in ``markdown`` format.
   If a custom format is named ``text``, it will inherit from the built-in
   ``text`` format instead.
   """
   markup: str
   """Selects the markup type.

   Currently supported types:

      * ``text`` - Plain text
      * ``markdown`` - Markdown

   The default Markdown configuration uses the Pandoc / Quarto dialect, but
   the output can be made compatible with the dialect used by GitHub using the
   other configuration options in this object.
   """
   underline: UnderlineDescriptor
   """When ``%(underline)s`` is used in most format strings, this will be used
   to format the underline.
   """
   toc_line: str
   """How to render a package line in the table of contents.

   Accepted placeholders:

      * ``%(name)s``: The name of the package.
      * ``%(versions)s``: The version(s) of the package.
      * ``%(license)s``: A comma-separated list of short license names.
   """
   shared_license: str
   """How to render the text of a shared license.

   Accepted placeholders:

      * ``%(name)s``: The long name of the license.
      * ``%(license)s``: The full body text of the license.
      * ``%(underline)s``: An underline based on :py:attr:`underline`.
   """
   package: str
   """How to render the description of a dependency package.

   Accepted placeholders:

      * ``%(name)s``: The name of the package.
      * ``%(versions)s``: The version(s) of the package.
      * ``%(url)s``: The URL where the package can be found.
      * ``%(attribution)s``: The copyright attribution messages. Each
         message is formatted using :py:attr:`attribution-line`.
      * ``%(message)s``: "Distributed under" messages for each license.
         Each message is formatted using :py:attr:`message-line`.
      * ``%(license)s``: The full body text of the license.
      * ``%(underline)s``: An underline based on :py:attr:`underline`.
   """
   attribution_line: str
   """How to render a line of copyright attribution. This formatted line will
   be inserted into the ``%(attribution)s`` placeholder in :py:attr:`package`.

   Accepted placeholder:

      * ``%(message)s``: The copyright attribution message.
   """
   message_line: str
   """How to render a line of distribution information. This formatted line
   will be inserted into the ``%(message)s`` placeholder in :py:attr:`package`.

   Accepted placeholder:

      * ``%(message)s``: The license distribution message.
   """
   license_line: str
   multi_license_lines: str
   multi_license_indent: str
   license_header_underline: UnderlineDescriptor
   nameless_license: str
   named_license: str
   multi_license: str
   license_indent: str
   license_blockquote: bool


_default_text_format = FormatDict({
   'markup': 'text',
   'underline': UnderlineDescriptor({'char': '='}),
   'toc_line': '* %(name)s%(versions)s (%(licenses)s)',
   'shared_license': """
%(name)s
%(underline)s
%(text)s""",
   'package': """
%(name)s%(versions)s
%(underline)s
Website: %(url)s

%(attribution)s
%(messages)s
%(license)s""",
   'attribution_line': '%(message)s',
   'message_line': '%(message)s',
   'license_line': 'Distributed under the %(name)s',
   'multi_license_lines': """
Distributed under multiple software licenses, including:
%(licenses)s
Consult the documentation and source code of %(package)s for more information.""",
   'multi_license_indent': '    ',
   'license_header_underline': UnderlineDescriptor({'char': '-'}),
   'nameless_license': """

License text:
%(underline)s
%(text)s
""",
   'named_license': """

%(name)s text:
%(underline)s
%(text)s
""",
   'multi_license': """

License text (%(names)s):
%(underline)s
%(text)s
""",
   'license_indent': '',
   'license_blockquote': False,
})

_default_markdown_format = FormatDict({
   'markup': 'markdown',
   'underline': UnderlineDescriptor({'char': '='}),
   'toc_line': '- %(name)s%(versions)s (%(licenses)s)',
   'shared_license': """
### %(name)s

%(text)s
""",
   'package': """
### [%(name)s](%(url)s)%(versions)s
%(attribution)s
%(messages)s
%(license)s""",
   'attribution_line': '- %(message)s',
   'message_line': '- %(message)s',
   'license_line': '- Distributed under the %(name)s',
   'multi_license_lines': """
- Distributed under multiple software licenses, including:
%(licenses)s
- Consult the documentation and source code of %(package)s for more information.""",
   'multi_license_indent': '  - ',
   'nameless_license': """
**License text:**

%(text)s
""",
   'named_license': """
**%(name)s text:**

%(text)s
""",
   'multi_license': """
**License text (%(names)s):**

%(text)s
""",
   'license_indent': '',
   'license_blockquote': True,
})

FORMATS: dict[str, 'FormatDict'] = {
   'text': _default_text_format,
   'markdown': _default_markdown_format,
}


class DocumentDict(TypedDict, total=False):
   """Configuration for a document to be rendered."""

   template: str
   """Path to the template file. Absolute at runtime; relative to the config
   file in the config file.
   """
   destination: str
   """Path to the output file. Absolute at runtime; relative to the config
   file in the config file.
   """
   format: str
   """Key identifying which :py:class:`FormatDict` to use."""
   exclude: str
   """If set, packages rendered in the named :py:class:`DocumentDict` will not
   be rendered in this document. This can be used to generate supplemental
   documents.
   """


def underline(underline: UnderlineDescriptor, context: dict[str, str]) -> str:
   """Generate an underline.

   :param underline: The underline format descriptor
   :param context: Variables that can inform the underline
   :return: An ASCII underline
   """
   if 'length' in underline:
      return underline['length'] * underline['char']
   return len(context['line']) * underline['char']


def _load_format_config(name: str, config: ConfigFile) -> FormatDict:
   """Parse a single format config out of a [formats] block.

   :param name: The format name, used for selecting defaults
   :param config: A group in the [formats] block
   :raises TypeError: if a value is of the wrong data type
   :raises KeyError: if an unexpected key is found
   :return: The parsed format descriptor
   """
   if name in FORMATS:
      fmt = copy.deepcopy(FORMATS[name])
   else:
      inherit = config.value('inherit', 'text')
      if inherit not in FORMATS:
         raise KeyError(f'Format {name} inherits from unknown format "{inherit}"')
      fmt = copy.deepcopy(FORMATS[inherit])
   for key in config.keys():
      if key == 'inherit':
         continue
      value = config.value(key)
      if key == 'markup' and value not in {'text', 'markdown'}:
         raise KeyError(f'Unknown markup type "{value}" in format {name}')
      if key in fmt:
         if type(value) is str and type(fmt[key]) is str:
            fmt[key] = value
         elif isinstance(fmt[key], dict):
            # only dicts right now are UnderlineDescriptor
            if type(value.get('length', -1)) is not int:
               raise TypeError(f'{key}.length expected int')
            if type(value.get('char', '-')) is not str:
               raise TypeError(f'{key}.char expected str')
            fmt[key] = UnderlineDescriptor({
               'length': value.get('length', -1),
               'char': value.get('char', '-'),
            })
      else:
         raise KeyError(f'unexpected {key} in format {name}')
   return fmt


def populate_formats(config: ConfigFile):
   """Validate and populate the FORMATS dict from the config file.

   :param config: The config file's [formats] group
   """
   for key in config.keys():
      fmt = _load_format_config(key, config.required_group(key))
      FORMATS[key] = fmt


def _load_document_config(key: str, config: ConfigFile) -> DocumentDict:
   """Parse a single document config out of an [options] block.

   :param key: The name of the output
   :param config: The config file group
   :raises FileNotFoundError: if the template does not exist
   :raises KeyError: if there are missing configuration keys
   :return: A parsed document description
   """
   template = config.relative_path(config.value('template'))
   if not os.path.exists(template):
      raise FileNotFoundError(template)

   if not config.value('destination'):
      raise KeyError(f'output.{key}: destination required')
   dest = config.relative_path(config.value('destination'))

   doc = DocumentDict({
      'template': template,
      'destination': dest,
   })

   if 'format' in config:
      if type(config.value('format')) is not str:
         raise TypeError('format expected str')
      doc['format'] = config.value('format')

   if 'exclude' in config:
      if type(config.value('exclude')) is not str:
         raise TypeError('exclude expected str')
      doc['exclude'] = config.value('exclude')

   return doc


def populate_outputs(config: ConfigFile):
   """Validate and populate the OUTPUTS dict from the config file.

   :param config: The config file's [output] group
   """
   for key in config.keys():
      doc = _load_document_config(key, config.required_group(key))
      OUTPUTS[key] = doc
