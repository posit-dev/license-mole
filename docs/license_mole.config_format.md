<a id="module-license_mole.config_format"></a>

<a id="license-mole-config-format-module"></a>

# license_mole.config_format module

Format configuration information.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.config_format.DocumentDict"></a>

### *class* license_mole.config_format.DocumentDict

Bases: `TypedDict`

Configuration for a document to be rendered.

<a id="license_mole.config_format.DocumentDict.destination"></a>

#### destination *: str*

Path to the output file. Absolute at runtime; relative to the config
file in the config file.

<a id="license_mole.config_format.DocumentDict.exclude"></a>

#### exclude *: str*

If set, packages rendered in the named [`DocumentDict`](#license_mole.config_format.DocumentDict) will not
be rendered in this document. This can be used to generate supplemental
documents.

<a id="license_mole.config_format.DocumentDict.format"></a>

#### format *: str*

Key identifying which [`FormatDict`](#license_mole.config_format.FormatDict) to use.

<a id="license_mole.config_format.DocumentDict.template"></a>

#### template *: str*

Path to the template file. Absolute at runtime; relative to the config
file in the config file.

<a id="license_mole.config_format.FormatDict"></a>

### *class* license_mole.config_format.FormatDict

Bases: `TypedDict`

Definitions for how to render portions of a document.

There are two built-in format definitions: `text` and `markdown`.

<a id="license_mole.config_format.FormatDict.attribution_line"></a>

#### attribution_line *: str*

How to render a line of copyright attribution. This formatted line will
be inserted into the `%(attribution)s` placeholder in [`package`](#license_mole.config_format.FormatDict.package).

Accepted placeholder:

> * `%(message)s`: The copyright attribution message.

<a id="license_mole.config_format.FormatDict.inherit"></a>

#### inherit *: str*

Specifies another format definition to inherit from.

Any options not specified will use the value from the inherited format.

By default, custom formats inherit from the built-in `markdown` format.
If a custom format is named `text`, it will inherit from the built-in
`text` format instead.

<a id="license_mole.config_format.FormatDict.license_blockquote"></a>

#### license_blockquote *: bool*

<a id="license_mole.config_format.FormatDict.license_header_underline"></a>

#### license_header_underline *: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor)*

<a id="license_mole.config_format.FormatDict.license_indent"></a>

#### license_indent *: str*

<a id="license_mole.config_format.FormatDict.license_line"></a>

#### license_line *: str*

<a id="license_mole.config_format.FormatDict.markup"></a>

#### markup *: str*

Selects the markup type.

Currently supported types:

> * `text` - Plain text
> * `markdown` - Markdown

The default Markdown configuration uses the Pandoc / Quarto dialect, but
the output can be made compatible with the dialect used by GitHub using the
other configuration options in this object.

<a id="license_mole.config_format.FormatDict.message_line"></a>

#### message_line *: str*

How to render a line of distribution information. This formatted line
will be inserted into the `%(message)s` placeholder in [`package`](#license_mole.config_format.FormatDict.package).

Accepted placeholder:

> * `%(message)s`: The license distribution message.

<a id="license_mole.config_format.FormatDict.multi_license"></a>

#### multi_license *: str*

<a id="license_mole.config_format.FormatDict.multi_license_indent"></a>

#### multi_license_indent *: str*

<a id="license_mole.config_format.FormatDict.multi_license_lines"></a>

#### multi_license_lines *: str*

<a id="license_mole.config_format.FormatDict.named_license"></a>

#### named_license *: str*

<a id="license_mole.config_format.FormatDict.nameless_license"></a>

#### nameless_license *: str*

<a id="license_mole.config_format.FormatDict.package"></a>

#### package *: str*

How to render the description of a dependency package.

Accepted placeholders:

> * `%(name)s`: The name of the package.
> * `%(versions)s`: The version(s) of the package.
> * `%(url)s`: The URL where the package can be found.
> * `%(attribution)s`: The copyright attribution messages. Each
>   : message is formatted using `attribution-line`.
> * `%(message)s`: “Distributed under” messages for each license.
>   : Each message is formatted using `message-line`.
> * `%(license)s`: The full body text of the license.
> * `%(underline)s`: An underline based on [`underline`](#license_mole.config_format.underline).

<a id="license_mole.config_format.FormatDict.shared_license"></a>

#### shared_license *: str*

How to render the text of a shared license.

Accepted placeholders:

> * `%(name)s`: The long name of the license.
> * `%(license)s`: The full body text of the license.
> * `%(underline)s`: An underline based on [`underline`](#license_mole.config_format.underline).

<a id="license_mole.config_format.FormatDict.toc_line"></a>

#### toc_line *: str*

How to render a package line in the table of contents.

Accepted placeholders:

> * `%(name)s`: The name of the package.
> * `%(versions)s`: The version(s) of the package.
> * `%(license)s`: A comma-separated list of short license names.

<a id="license_mole.config_format.FormatDict.underline"></a>

#### underline *: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor)*

When `%(underline)s` is used in most format strings, this will be used
to format the underline.

<a id="license_mole.config_format.UnderlineDescriptor"></a>

### *class* license_mole.config_format.UnderlineDescriptor

Bases: `TypedDict`

Description of how text should be underlined.

<a id="license_mole.config_format.UnderlineDescriptor.char"></a>

#### char *: str*

The character used to render the underline. Typically `-` or `=`.

<a id="license_mole.config_format.UnderlineDescriptor.length"></a>

#### length *: int*

If specified, the underline is rendered as this many copies of
[`char`](#license_mole.config_format.UnderlineDescriptor.char). If omitted, the underline is rendered to the width of
the previous line of text.

<a id="license_mole.config_format.populate_formats"></a>

### license_mole.config_format.populate_formats(config: [ConfigFile](license_mole.configfile.md#license_mole.configfile.ConfigFile))

Validate and populate the FORMATS dict from the config file.

* **Parameters:**
  **config** – The config file’s [formats] group

<a id="license_mole.config_format.populate_outputs"></a>

### license_mole.config_format.populate_outputs(config: [ConfigFile](license_mole.configfile.md#license_mole.configfile.ConfigFile))

Validate and populate the OUTPUTS dict from the config file.

* **Parameters:**
  **config** – The config file’s [output] group

<a id="license_mole.config_format.underline"></a>

### license_mole.config_format.underline(underline: [UnderlineDescriptor](#license_mole.config_format.UnderlineDescriptor), context: dict[str, str]) → str

Generate an underline.

* **Parameters:**
  * **underline** – The underline format descriptor
  * **context** – Variables that can inform the underline
* **Returns:**
  An ASCII underline
