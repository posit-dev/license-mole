# license_mole.render.context module

Container for shared rendering information.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.render.context.LicenseContext(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict))

Bases: `object`

A minimal container for tracking license usage across packages.

#### excluded *: set[str]*

#### format *: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict)*

#### license_usage *: dict[str, set[str]]*

#### markdown *: bool*

#### render_license(path: str) → str

Render a license file as a blockquote.

* **Parameters:**
  **path** – Path to the license file
* **Returns:**
  Formatted Markdown text

#### shared_licenses *: dict[str, str]*
