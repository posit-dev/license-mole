# license_mole.licenses.collection module

Functions for managing a collection of licenses for a package.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.licenses.collection.LicenseCollection(package: str, base_path: str, author: str | None = None)

Bases: `object`

A collection of licenses for a package.

* **Variables:**
  * **links** – Mapping from normalized license identifier to file paths
  * **files** – Mapping from file paths to license descriptions.
    See analyze_license_file for details.
* **Parameters:**
  * **package** – The package identifier (see BasePackage.key)
  * **base_path** – The directory containing the package
  * **author** – The author of the package, if known

#### add(ltype_or_ltypes: str | tuple[str, ...])

Add a license identifier to the collection.

* **Parameters:**
  **ltype_or_ltypes** – License identifier(s) to add
* **Raises:**
  **ValueError** – if a license identifier is invalid

#### add_file(path: str) → [LicenseInfo](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo)

Add a file to the collection.

If the license contains an SPDX identifier or can be unambiguously
identified from its filename, the file is linked to the corresponding
license identifier.

This function returns the result of analyzing the file.

* **Parameters:**
  **path** – Path to the license file
* **Returns:**
  License file description (see analyze_license_file)

#### add_file_from_cache(path: str, cached: dict[str, Any])

Add a file to the collection based on cached data.

* **Parameters:**
  * **path** – Path to the license file
  * **cached** – Data from the cache

#### *property* attribution *: list[str]*

A list of copyright attribution lines.

Typically these lines are in the form “Copyright (c) <year> <author>”.

#### auto_link_files() → bool

Heuristically links license files to license identifiers.

If any files in the collection have an unambiguous SPDX identifier, they
are linked to those identifiers in the collection.

If the collection only contains one unlinked identifier and one unlinked
file, they are linked and this association is added to the main license
registry. This may raise LicenseConflictError if the content of the file
does not match the license identifier.

* **Raises:**
  [**LicenseConflictError**](license_mole.errors.md#license_mole.errors.LicenseConflictError) – if the license file has been seen with a
  different identifier
* **Returns:**
  True if all licenses in the collection have been linked

#### count_unlinked() → tuple[int, int]

Return the number of unlinked license identifiers and unlinked files.

#### files *: dict[str, [LicenseInfo](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo)]*

#### get_attribution_from_files() → list[str]

Collect attribution lines from associated files.

Unlike the attribution property, this is not cached.

* **Returns:**
  A list of copyright atribution lines.

#### get_file(ltype: str) → str | None

Return the license file linked to an identifier.

* **Parameters:**
  **ltype** – The license identifier
* **Returns:**
  The path to the license file, if known

#### has(ltype: str) → bool

Check to see if the collection contains the requested license.

* **Parameters:**
  **ltype** – The license identifier
* **Returns:**
  Whether the collection contains the license

#### is_empty() → bool

Return True if the collection contains no license information.

#### link_file(ltype: str, path: str) → bool

Links a license file to a license type.

If the file was already linked to the identifier, this function does
nothing and returns False.

If the identifier was not linked to a file, this function returns False.

If there was already a link to a different license file, this function
chooses whether to keep the old link or replace it with the new link.
In either case, this function returns True.

* **Parameters:**
  * **ltype** – The license identifier for the file
  * **path** – The path to the license file
* **Returns:**
  True if there was already a link to a different license file

#### links *: dict[str, str]*

#### *property* unlinked_files *: dict[str, [LicenseInfo](license_mole.licenses.parse.md#license_mole.licenses.parse.LicenseInfo)]*

A list of files that have not been matched with a license identifier.

#### *property* unlinked_ltypes *: list[str]*

A list of license identifiers that have not been matched with a file.

### license_mole.licenses.collection.normalize_license_url(url: str) → str

Clean up a URL pointing to a license file.

The returned URL should be plain text (not HTML) and ideally retrieved
over HTTPS instead of HTTP. The URL is not guaranteed to exist.

If the provided path is not a URL, it is returned unchanged.

* **Parameters:**
  **url** – The URL to clean
* **Returns:**
  The cleaned URL
