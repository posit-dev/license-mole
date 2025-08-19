# license_mole.render.package module

Functions to represent information about how components should be rendered.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.render.package.RenderPackage(source: [BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage) | dict[str, Any], group: str)

Bases: `object`

A description of a package for rendering.

This is not a BasePackage and cannot participate in dependency or license
resolution.

This class can collect information from a BasePackage or from a JSON cache.
It can output a dictionary suitable for storing in a JSON cache.

* **Parameters:**
  * **source** – The package to render
  * **group** – The functional group containing the package

#### comparison_key() → tuple[str | int, ...]

Produce a comparison key for sorting packages.

The resulting sort order is:
\* Ascending by package name
\* Descending by version number

* **Returns:**
  A comparison key

#### merge(other: [RenderPackage](#license_mole.render.package.RenderPackage))

Combine another RenderPackage into this one.

* **Parameters:**
  **other** – The package to be combined
* **Raises:**
  **ValueError** – if the package to be merged is incompatible

#### render(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), show_versions: list[str]) → str

Render a one-line package summary in Markdown.

* **Parameters:**
  * **fmt** – Description of the rendering format
  * **show_versions** – A list of version numbers to display
* **Returns:**
  Markdown-formatted text

#### render_long(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), show_versions: list[str], context: [LicenseContext](license_mole.render.context.md#license_mole.render.context.LicenseContext)) → str

Render full attribution and licensing in Markdown to stdout.

* **Parameters:**
  * **fmt** – Description of the rendering format
  * **show_versions** – A list of version numbers to display
  * **context** – The context containing shared license information
* **Returns:**
  A block of Markdown text

#### to_dict() → dict[str, Any]

Serialize this object.

* **Returns:**
  A dictionary suitable for serialization

#### *property* unversioned *: str*

The package key with version removed.

### license_mole.render.package.attribution_comparison_key(attrs: list[str]) → tuple[str, ...]

Create a comparison key for a list of attributions.

Two packages with the same attribution comparison key have the same set of
authors, but copyright dates may have different years.

* **Parameters:**
  **attrs** – List of attributions
* **Returns:**
  An attribution comparison key

### license_mole.render.package.normalize_ltype(ltype: str) → str

Normalize a license type for rendering comparison.

This does not remove variants like normalize_ltype_for_comparison does.
It does unify “LLVM Exception” and “LLVM Exceptions”.

* **Parameters:**
  **ltype** – The license type
* **Returns:**
  Normalized license type

### license_mole.render.package.populate_template(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), template_key: str, args: dict[str, str], underline_key: str = 'underline') → str

Interpolate args into a template, calculating an underline if necessary.

If `%(underline)s` appears more than once in the template, the last one
to appear will be used to determine the line length. This allows the use of
an underline for box drawing.

* **Parameters:**
  * **fmt** – The formatting definition to be used
  * **template_key** – The key into `fmt` containing the template
  * **args** – The string interpolation arguments for the template
  * **underline_key** – Which underline definition from `fmt` to use
* **Returns:**
  Text suitable for use as an underline
