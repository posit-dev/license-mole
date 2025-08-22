<a id="module-license_mole.render.context"></a>

<a id="license-mole-render-context-module"></a>

# license_mole.render.context module

Container for shared rendering information.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.render.context.LicenseContext"></a>

### *class* license_mole.render.context.LicenseContext(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict))

Bases: `object`

A minimal container for tracking license usage across packages.

<a id="license_mole.render.context.LicenseContext.excluded"></a>

#### excluded *: set[str]*

<a id="license_mole.render.context.LicenseContext.format"></a>

#### format *: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict)*

<a id="license_mole.render.context.LicenseContext.license_usage"></a>

#### license_usage *: dict[str, set[str]]*

<a id="license_mole.render.context.LicenseContext.markdown"></a>

#### markdown *: bool*

<a id="license_mole.render.context.LicenseContext.render_license"></a>

#### render_license(path: str) → str

Render a license file as a blockquote.

* **Parameters:**
  **path** – Path to the license file
* **Returns:**
  Formatted Markdown text

<a id="license_mole.render.context.LicenseContext.shared_licenses"></a>

#### shared_licenses *: dict[str, str]*
