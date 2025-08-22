<a id="module-license_mole.licenses"></a>

<a id="license-mole-licenses-package"></a>

# license_mole.licenses package

Functions for locating license files.

Copyright (c) 2025 Posit Software, PBC

By convention, the name `ltype` is used to refer to an SPDX-style license
identifier across the codebase.

<a id="license_mole.licenses.LicenseRegistry"></a>

### *class* license_mole.licenses.LicenseRegistry

Bases: `object`

Singleton registry for identified license files.

This class is used for heuristically comparing license texts to each other
to determine if they refer to the same license, and for providing a path
to a license file if only a license identifier is known.

<a id="license_mole.licenses.LicenseRegistry.add"></a>

#### add(ltype: str, license_info: [LicenseInfo](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo), source_pkg: str)

Add a license to the registry.

* **Parameters:**
  * **ltype** – License identifier
  * **license_info** – Output of `analyze_license_file`
  * **source_pkg** – Package identifier containing license file
* **Raises:**
  [**LicenseConflictError**](license_mole.errors.md#license_mole.errors.LicenseConflictError) – if the license file is already known under a
  different license identifier.

<a id="license_mole.licenses.LicenseRegistry.get_file_for_type"></a>

#### get_file_for_type(ltype: str, attribution: list[str] | None = None) → str | None

Return the path to a copy of the text for a license.

Only “clean” license files are candidates for this search. A “clean”
license file does not contain any copyright information specific to any
author or package. This is intended to be suitable to be applied to any
package with the same license.

* **Parameters:**
  * **ltype** – License identifier
  * **attribution** – Copyright attribution, if known
* **Returns:**
  Path to the license file, if known

<a id="license_mole.licenses.LicenseRegistry.get_source_for_checksum"></a>

#### get_source_for_checksum(cs: str) → tuple[str, str] | None

Return a source tuple identifying where a license file was first seen.

* **Parameters:**
  **cs** – The checksum of the normalized license file contents
* **Returns:**
  Package and file containing license, if known

<a id="license_mole.licenses.LicenseRegistry.get_type_by_checksum"></a>

#### get_type_by_checksum(cs: str) → str | None

Return the license identifier registered for a license file.

* **Parameters:**
  **cs** – The checksum of the normalized license file contents
* **Returns:**
  The license identifier, if known

<a id="license_mole.licenses.find_license_files"></a>

### license_mole.licenses.find_license_files(path: str) → list[str]

Look for license files in a directory.

A file is considered a license file if it contains (case-insensitive)
any of the words “LICENSE”, “LICENCE”, or “COPYING”, or if the filename
is (case-insensitive) “COPYRIGHT”, optionally with a file extension.

License files should only contain license information. Readme files and
source code files are not license information and should not be returned.

* **Parameters:**
  **path** – Directory to search
* **Returns:**
  List of detected license files

<a id="license_mole.licenses.normalize_ltype_for_comparison"></a>

### license_mole.licenses.normalize_ltype_for_comparison(ltype: str) → str

Normalize an ltype into a form suitable for comparison.

We preserve the format that the package author chose to use for rendering,
but for comparisons we convert license identifiers into a normalized form.

* **Parameters:**
  **ltype** – License identifier to normalize
* **Returns:**
  Normalized license identifier

<a id="license_mole.licenses.scan_repo_for_license"></a>

### license_mole.licenses.scan_repo_for_license(repo_url: str) → str

Check a source code repository for a license file.

The license file is downloaded if it is found, so a subsequent call to
`download_file_cached` is guaranteed to find it in the cache.

* **Parameters:**
  **repo_url** – URL to the source code repository
* **Returns:**
  The URL to the license file

* [license_mole.licenses.resources package](license_mole.licenses.resources.md)
  * [`get_standard_license_reference()`](license_mole.licenses.resources.md#license_mole.licenses.resources.get_standard_license_reference)
  * [`get_standard_license_text()`](license_mole.licenses.resources.md#license_mole.licenses.resources.get_standard_license_text)
  * [`is_safe_license_text()`](license_mole.licenses.resources.md#license_mole.licenses.resources.is_safe_license_text)

* [license_mole.licenses.collection module](license_mole.licenses.collection.md)
  * [`LicenseCollection`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection)
    * [`LicenseCollection.add()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.add)
    * [`LicenseCollection.add_file()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.add_file)
    * [`LicenseCollection.add_file_from_cache()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.add_file_from_cache)
    * [`LicenseCollection.attribution`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.attribution)
    * [`LicenseCollection.auto_link_files()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.auto_link_files)
    * [`LicenseCollection.count_unlinked()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.count_unlinked)
    * [`LicenseCollection.files`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.files)
    * [`LicenseCollection.get_attribution_from_files()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.get_attribution_from_files)
    * [`LicenseCollection.get_file()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.get_file)
    * [`LicenseCollection.has()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.has)
    * [`LicenseCollection.is_empty()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.is_empty)
    * [`LicenseCollection.link_file()`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.link_file)
    * [`LicenseCollection.links`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.links)
    * [`LicenseCollection.unlinked_files`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.unlinked_files)
    * [`LicenseCollection.unlinked_ltypes`](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection.unlinked_ltypes)
  * [`normalize_license_url()`](license_mole.licenses.collection.md#license_mole.licenses.collection.normalize_license_url)
* [license_mole.licenses.parse module](license_mole.licenses.parse.md)
  * [`LicenseInfo`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo)
    * [`LicenseInfo.attribution`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.attribution)
    * [`LicenseInfo.author`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.author)
    * [`LicenseInfo.checksum`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.checksum)
    * [`LicenseInfo.clean`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.clean)
    * [`LicenseInfo.guess`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.guess)
    * [`LicenseInfo.multi`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.multi)
    * [`LicenseInfo.path`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.path)
    * [`LicenseInfo.spdx`](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo.spdx)
  * [`analyze_license_file()`](license_mole.licenses.parse.md#license_mole.licenses.parse.analyze_license_file)
  * [`get_license_text()`](license_mole.licenses.parse.md#license_mole.licenses.parse.get_license_text)
  * [`get_readme_attribution()`](license_mole.licenses.parse.md#license_mole.licenses.parse.get_readme_attribution)
  * [`normalize_license_code()`](license_mole.licenses.parse.md#license_mole.licenses.parse.normalize_license_code)
