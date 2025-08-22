<a id="module-license_mole.errors"></a>

<a id="license-mole-errors-module"></a>

# license_mole.errors module

Exception classes used across license-mole.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.errors.HomepageMissingError"></a>

### *exception* license_mole.errors.HomepageMissingError(key: str)

Bases: `RuntimeError`

Error raised when a package’s homepage cannot be resolved.

* **Parameters:**
  **key** – package identifier

<a id="license_mole.errors.LicenseConflictError"></a>

### *exception* license_mole.errors.LicenseConflictError(ltype: str, source: tuple[str, str], new_ltype: str, new_source: tuple[str, str])

Bases: `RuntimeError`

Error raised when a license file disagrees with existing information.

* **Parameters:**
  * **ltype** – Identifier of known license
  * **source** – Package and file where known license was found
  * **new_ltype** – Identifier of newly-found license
  * **new_source** – Package and file containing newly-found license

<a id="license_mole.errors.LicenseValidationError"></a>

### *exception* license_mole.errors.LicenseValidationError

Bases: `RuntimeError`

Error raised while validating licenses.

This can be caused by failing to find license text for a license type,
failing to identify the license type for a license file, or failing to
identify copyright attribution for a package.

<a id="license_mole.errors.MissingPackageError"></a>

### *exception* license_mole.errors.MissingPackageError(msg: str | None)

Bases: `RuntimeError`

Error raised when a named dependency can’t be found.

* **Parameters:**
  **msg** – Description of the dependency chain leading to the missing package

<a id="license_mole.errors.NoLicenseError"></a>

### *exception* license_mole.errors.NoLicenseError(key: str)

Bases: `RuntimeError`

Error raised when package metadata does not contain license information.

* **Parameters:**
  **key** – Package identifier

<a id="license_mole.errors.UnidentifiedLicenseError"></a>

### *exception* license_mole.errors.UnidentifiedLicenseError(key: str, path: str)

Bases: `RuntimeError`

Error raised when a package’s licensing cannot be identified.

For this exception to be raised, the package must not have any license
identifiers in its metadata, it must have a license file, and the
heuristics cannot identify the license file.

* **Parameters:**
  * **key** – Package identifier
  * **path** – Full path to license file
