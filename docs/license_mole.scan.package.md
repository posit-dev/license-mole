<a id="module-license_mole.scan.package"></a>

<a id="license-mole-scan-package-module"></a>

# license_mole.scan.package module

Base class for package descriptions.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.scan.package.BasePackage"></a>

### *class* license_mole.scan.package.BasePackage(name: str, path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector), version: str = '', author: str = '', scan: bool = True)

Bases: `object`

Base class for package descriptions.

The constructor scans the package directory for license files.

Subclasses should be careful to honor values found in py:attr:`self._overrides`.

* **Parameters:**
  * **name** – The display name of the package
  * **path** – The path containing the package’s files
  * **version** – The version of the package, if known
  * **author** – The author of the package, if known
  * **scan** – If False, disables automatic scanning for license files

<a id="license_mole.scan.package.BasePackage.deserialize"></a>

#### *classmethod* deserialize(data: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → Self

Construct a package from serialized data.

* **Parameters:**
  * **data** – Serialized data
  * **selector** – The selector that paths are relative to
* **Returns:**
  A new package instance

<a id="license_mole.scan.package.BasePackage.ignored"></a>

#### ignored *: bool*

If True, completely ignore this package.

Scanners may choose to look for transitive dependencies in ignored packages.

<a id="license_mole.scan.package.BasePackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

Subclasses must implement this property.

Keys should be of the form `type::name[@version]`.

<a id="license_mole.scan.package.BasePackage.licenses"></a>

#### licenses *: [LicenseCollection](license_mole.licenses.collection.md#license_mole.licenses.collection.LicenseCollection)*

Information about detected licenses.

<a id="license_mole.scan.package.BasePackage.name"></a>

#### name *: str*

Human-readable name of the package.

<a id="license_mole.scan.package.BasePackage.package_type"></a>

#### package_type *: str*

Label for rendering what kind of package this is.

<a id="license_mole.scan.package.BasePackage.path"></a>

#### path *: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)*

Path to the root of the package.

<a id="license_mole.scan.package.BasePackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

Subclasses should override this to add additional fields.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.package.BasePackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

Ideally this should be a link to the source code repository, but
a link to a package page is acceptable.

Subclasses must implement this property.

<a id="license_mole.scan.package.BasePackage.version"></a>

#### version *: str | None*

The version of the package.

<a id="license_mole.scan.package.BasePackage.version_tuple"></a>

#### *property* version_tuple *: tuple[int, ...]*

A tuple suitable for comparing package versions.

<a id="license_mole.scan.package.version_tuple"></a>

### license_mole.scan.package.version_tuple(version: str | None) → tuple[int, ...]

Split a version into a tuple suitable for sorting.

* **Parameters:**
  **version** – The package’s version string
* **Returns:**
  A tuple of version components
