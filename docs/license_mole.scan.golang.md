# license_mole.scan.golang module

Functions for collecting Go packages.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.scan.golang.GoModule(pkg: dict[str, Any])

Bases: `object`

A basic wrapper around the JSON response from go list.

* **Parameters:**
  **pkg** – Parsed JSON

### *class* license_mole.scan.golang.GoPackage(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector), mod: [GoModule](#license_mole.scan.golang.GoModule))

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a Go package.

A package is a collection of modules deployed together under a single name.

* **Parameters:**
  * **selector** – Path selector for the parent package
  * **mod** – Parsed package information from go list

#### *property* key *: str*

A unique key identifying the package.

#### package_type *= 'Go'*

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

#### *property* url *: str*

The URL to a “homepage” for the package.

### *class* license_mole.scan.golang.GoScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects Go packages and their dependencies.

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

#### package_type *= 'Go'*

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan a Go project for dependency information.

Dependencies are collected into packages so that submodules contained
in a single repository under a single license are presented as one
entry for reporting.

Collected packages are stored in self.packages.

* **Parameters:**
  **path** – The path to the Go project root
* **Raises:**
  [**NoLicenseError**](license_mole.errors.md#license_mole.errors.NoLicenseError) – if a package’s metadata has no licensing data

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
