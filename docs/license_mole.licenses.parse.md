<a id="module-license_mole.licenses.parse"></a>

<a id="license-mole-licenses-parse-module"></a>

# license_mole.licenses.parse module

Functions for heuristically parsing license files.

Copyright (c) 2025 Posit Software, PBC

By convention, the name `ltype` is used to refer to an SPDX-style license
identifier across the codebase.

<a id="license_mole.licenses.parse.LicenseInfo"></a>

### *class* license_mole.licenses.parse.LicenseInfo

Bases: `TypedDict`

Heuristic description of a license file.

<a id="license_mole.licenses.parse.LicenseInfo.attribution"></a>

#### attribution *: list[str]*

Detected copyright attribution lines

<a id="license_mole.licenses.parse.LicenseInfo.author"></a>

#### author *: str | None*

The author passed into this function

<a id="license_mole.licenses.parse.LicenseInfo.checksum"></a>

#### checksum *: str*

The checksum of the normalized license text

<a id="license_mole.licenses.parse.LicenseInfo.clean"></a>

#### clean *: bool*

File can be reused for other packages

<a id="license_mole.licenses.parse.LicenseInfo.guess"></a>

#### guess *: str | None*

Heuristically-inferred SPDX identifier, if any

<a id="license_mole.licenses.parse.LicenseInfo.multi"></a>

#### multi *: bool*

File has multiple detected licenses inside

<a id="license_mole.licenses.parse.LicenseInfo.path"></a>

#### path *: str*

The path passed into this function

<a id="license_mole.licenses.parse.LicenseInfo.spdx"></a>

#### spdx *: tuple[str, ...]*

Unambiguously-detected SPDX identifiers

<a id="license_mole.licenses.parse.analyze_license_file"></a>

### license_mole.licenses.parse.analyze_license_file(path: str, author: str | None = '', ignore_uncertain: bool = False) → [LicenseInfo](#license_mole.licenses.parse.LicenseInfo)

Load and analyzes a license file to collect heuristics.

* **Parameters:**
  * **path** – URL or path to license file
  * **author** – Author from package metadata, if known
  * **ignore_uncertain** – If True, suppresses warnings about uncertain attribution
* **Raises:**
  **ValueError** – if the file contains no license text
* **Returns:**
  License file description

<a id="license_mole.licenses.parse.get_license_text"></a>

### license_mole.licenses.parse.get_license_text(path: str) → str

Fetch the text of a license from a path/URL.

Newlines are normalized. Input is expected to be in UTF-8 format.

License paths support a special anchor format for extracting a license from a
larger text file based on text markers contained in the file. (It is not
recommended to use this on HTML files, and HTML anchors are not supported.)

> <url-or-path>#start        License text starts after the string “start”

> <url-or-path>#start#end    License text is between “start” and “end”
* **Parameters:**
  **path** – URL or path to license file
* **Returns:**
  The text of the license file

<a id="license_mole.licenses.parse.get_readme_attribution"></a>

### license_mole.licenses.parse.get_readme_attribution(path: str) → list[str]

Extract attribution lines from a readme file.

* **Parameters:**
  **path** – Path to readme file
* **Returns:**
  List of copyright attribution lines

<a id="license_mole.licenses.parse.normalize_license_code"></a>

### license_mole.licenses.parse.normalize_license_code(ltype: str) → tuple[str, ...]

Split a license identifier into a tuple of SPDX identifiers.

The result is suitable for rendering, but not for comparison.
See `licenses.normalize_ltype_for_comparison` for a normalization scheme
that will allow license identifiers to be compared to each other.

* **Parameters:**
  **ltype** – Non-normalized license identifier
* **Returns:**
  A tuple of license identifiers
