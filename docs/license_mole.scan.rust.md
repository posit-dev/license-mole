<a id="module-license_mole.scan.rust"></a>

<a id="license-mole-scan-rust-module"></a>

# license_mole.scan.rust module

Functions for collecting Rust packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.scan.rust.PackageGroupConflictError"></a>

### *exception* license_mole.scan.rust.PackageGroupConflictError(name: str, group1: [RustPackage](#license_mole.scan.rust.RustPackage), group2: [RustPackage](#license_mole.scan.rust.RustPackage))

Bases: `RuntimeError`

Raised when distinct package groups have the same name.

* **Parameters:**
  * **name** – The name of the package group
  * **group1** – The packages contained within the first group
  * **group2** – The packages contained within the second group

<a id="license_mole.scan.rust.RustBasicPackage"></a>

### *class* license_mole.scan.rust.RustBasicPackage(path: str, pkg: dict[str, Any])

Bases: `object`

A basic wrapper around the “package” section of Cargo.toml.

* **Parameters:**
  * **path** – Path to directory containing Cargo.toml
  * **pkg** – Parsed TOML

<a id="license_mole.scan.rust.RustBasicPackage.combine_key"></a>

#### *property* combine_key *: tuple[str, str, str, str]*

Returns a key that identifies if packages can be merged.

<a id="license_mole.scan.rust.RustPackage"></a>

### *class* license_mole.scan.rust.RustPackage(pkgs: list[[RustBasicPackage](#license_mole.scan.rust.RustBasicPackage)])

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a Rust package group.

A package group may be a single Cargo package, or multiple packages stored
within the same repository. This grouping was chosen to reduce repetition
in internal dependencies.

* **Parameters:**
  **pkgs** – Parsed package information

<a id="license_mole.scan.rust.RustPackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

<a id="license_mole.scan.rust.RustPackage.merge"></a>

#### merge(other: [RustPackage](#license_mole.scan.rust.RustPackage))

Merge the children of two packages.

* **Parameters:**
  **other** – The other package

<a id="license_mole.scan.rust.RustPackage.package_type"></a>

#### package_type *: str* *= 'Rust'*

Label for rendering what kind of package this is.

<a id="license_mole.scan.rust.RustPackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.rust.RustPackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

<a id="license_mole.scan.rust.RustScanner"></a>

### *class* license_mole.scan.rust.RustScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects Rust packages and their dependencies.

<a id="license_mole.scan.rust.RustScanner.compare_cache"></a>

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

<a id="license_mole.scan.rust.RustScanner.deserialize_cache"></a>

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

<a id="license_mole.scan.rust.RustScanner.package_type"></a>

#### package_type *= 'Rust'*

A descriptive label for the type of packages found by this scanner.

<a id="license_mole.scan.rust.RustScanner.scan"></a>

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → None

Scan a Rust project for dependency information.

Dependencies are collected into packages so that submodules contained
in a single repository under a single license are presented as one
entry for reporting.

Collected packages are stored in `self.packages`.

* **Parameters:**
  **path** – The path to the Rust project root
* **Raises:**
  [**NoLicenseError**](license_mole.errors.md#license_mole.errors.NoLicenseError) – if a package’s metadata has no licensing data

<a id="license_mole.scan.rust.RustScanner.serialize_cache"></a>

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
