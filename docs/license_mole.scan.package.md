# license_mole.scan.package module

Base class for package descriptions.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.scan.package.BasePackage(name: str, path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector), version: str = '', author: str = '', scan: bool = True)

Bases: `object`

Base class for package descriptions.

The constructor scans the package directory for license files.

Subclasses should be careful to honor values found in self._overrides.

* **Variables:**
  * **name** – Human-readable name of the package
  * **path** – Path to the root of the package
  * **version** – The version of the package
  * **licenses** – Information about detected licenses
  * **ignored** – If True, completely ignore this package.
* **Parameters:**
  * **name** – The display name of the package
  * **path** – The path containing the package’s files
  * **version** – The version of the package, if known
  * **author** – The author of the package, if known
  * **scan** – If False, disables automatic scanning for license files

#### *classmethod* deserialize(data: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → Self

Construct a package from serialized data.

* **Parameters:**
  * **data** – Serialized data
  * **selector** – The selector that paths are relative to
* **Returns:**
  A new package instance

#### ignored *: bool*

#### *property* key *: str*

A unique key identifying the package.

Subclasses must implement this property.

Keys should be of the form type::name[@version].

#### licenses *: [LicenseCollection](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection)*

#### name *: str*

#### path *: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)*

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

Subclasses should override this to add additional fields.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

#### *property* url *: str*

The URL to a “homepage” for the package.

Ideally this should be a link to the source code repository, but
a link to a package page is acceptable.

Subclasses must implement this property.

#### version *: str | None*
