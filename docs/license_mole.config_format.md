# license_mole.config_format module

Format configuration information.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.config_format.DocumentDict

Bases: `TypedDict`

Configuration for a document to be rendered.

#### destination *: str*

Path to the output file. Absolute at runtime; relative to the config
file in the config file.

#### exclude *: str*

If set, packages rendered in the named [`DocumentDict`](#license_mole.config_format.DocumentDict) will not
be rendered in this document. This can be used to generate supplemental
documents.

#### format *: str*

Key identifying which [`FormatDict`](#license_mole.config_format.FormatDict) to use.

#### template *: str*

Path to the template file. Absolute at runtime; relative to the config
file in the config file.

### *class* license_mole.config_format.FormatDict

Bases: `TypedDict`

Definitions for how to render portions of a document.

There are two built-in format definitions: `text` and `markdown`.

#### attribution_line *: str*

How to render a line of copyright attribution. This formatted line will
be inserted into the `%(attribution)s` placeholder in [`package`](#license_mole.config_format.FormatDict.package).

Accepted placeholder:

> * `%(message)s`: The copyright attribution message.

#### inherit *: str*

Specifies another format definition to inherit from.

Any options not specified will use the value from the inherited format.

By default, custom formats inherit from the built-in `markdown` format.
If a custom format is named `text`, it will inherit from the built-in
`text` format instead.

#### license_blockquote *: bool*

#### license_header_underline *: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor)*

#### license_indent *: str*

#### license_line *: str*

#### markup *: str*

Selects the markup type.

Currently supported types:

> * `text` - Plain text
> * `markdown` - Markdown

The default Markdown configuration uses the Pandoc / Quarto dialect, but
the output can be made compatible with the dialect used by GitHub using the
other configuration options in this object.

#### message_line *: str*

How to render a line of distribution information. This formatted line
will be inserted into the `%(message)s` placeholder in [`package`](#license_mole.config_format.FormatDict.package).

Accepted placeholder:

> * `%(message)s`: The license distribution message.

#### multi_license *: str*

#### multi_license_indent *: str*

#### multi_license_lines *: str*

#### named_license *: str*

#### nameless_license *: str*

#### package *: str*

How to render the description of a dependency package.

Accepted placeholders:

> * `%(name)s`: The name of the package.
> * `%(url)s`: The URL where the package can be found.
> * `%(attribution)s`: The copyright attribution messages. Each
>   : message is formatted using `attribution-line`.
> * `%(message)s`: “Distributed under” messages for each license.
>   : Each message is formatted using `message-line`.
> * `%(license)s`: The full body text of the license.
> * `%(underline)s`: An underline based on [`underline`](#license_mole.config_format.underline).

#### shared_license *: str*

How to render the text of a shared license.

Accepted placeholders:

> * `%(name)s`: The long name of the license.
> * `%(license)s`: The full body text of the license.
> * `%(underline)s`: An underline based on [`underline`](#license_mole.config_format.underline).

#### toc_line *: str*

How to render a package line in the table of contents.

Accepted placeholders:

> * `%(name)s`: The name of the package.
> * `%(license)s`: A comma-separated list of short license names.

#### underline *: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor)*

When `%(underline)s` is used in most format strings, this will be used
to format the underline.

### *class* license_mole.config_format.UnderlineDescriptor

Bases: `TypedDict`

Description of how text should be underlined.

#### char *: str*

The character used to render the underline. Typically `-` or `=`.

#### length *: int*

If specified, the underline is rendered as this many copies of
[`char`](#license_mole.config_format.UnderlineDescriptor.char). If omitted, the underline is rendered to the width of
the previous line of text.

### license_mole.config_format.populate_formats(config: [ConfigFile](license_mole.configfile.md#license_mole.configfile.ConfigFile))

Validate and populate the FORMATS dict from the config file.

* **Parameters:**
  **config** – The config file’s [formats] group

### license_mole.config_format.populate_outputs(config: [ConfigFile](license_mole.configfile.md#license_mole.configfile.ConfigFile))

Validate and populate the OUTPUTS dict from the config file.

* **Parameters:**
  **config** – The config file’s [output] group

### license_mole.config_format.underline(underline: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor), context: dict[str, str]) → str

Generate an underline.

* **Parameters:**
  * **underline** – The underline format descriptor
  * **context** – Variables that can inform the underline
* **Returns:**
  An ASCII underline
