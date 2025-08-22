<a id="module-license_mole.scan.golang"></a>

<a id="license-mole-scan-golang-module"></a>

# license_mole.scan.golang module

Functions for collecting Go packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.scan.golang.GoModule"></a>

### *class* license_mole.scan.golang.GoModule(pkg: dict[str, Any])

Bases: `object`

A basic wrapper around the JSON response from `go list`.

* **Parameters:**
  **pkg** – Parsed JSON

<a id="license_mole.scan.golang.GoPackage"></a>

### *class* license_mole.scan.golang.GoPackage(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector), mod: [GoModule](#license_mole.scan.golang.GoModule))

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a Go package.

A package is a collection of modules deployed together under a single name.

* **Parameters:**
  * **selector** – Path selector for the parent package
  * **mod** – Parsed package information from `go list`

<a id="license_mole.scan.golang.GoPackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

<a id="license_mole.scan.golang.GoPackage.package_type"></a>

#### package_type *: str* *= 'Go'*

Label for rendering what kind of package this is.

<a id="license_mole.scan.golang.GoPackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.golang.GoPackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

<a id="license_mole.scan.golang.GoScanner"></a>

### *class* license_mole.scan.golang.GoScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects Go packages and their dependencies.

<a id="license_mole.scan.golang.GoScanner.compare_cache"></a>

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

<a id="license_mole.scan.golang.GoScanner.deserialize_cache"></a>

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

<a id="license_mole.scan.golang.GoScanner.package_type"></a>

#### package_type *= 'Go'*

A descriptive label for the type of packages found by this scanner.

<a id="license_mole.scan.golang.GoScanner.scan"></a>

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan a Go project for dependency information.

Dependencies are collected into packages so that submodules contained
in a single repository under a single license are presented as one
entry for reporting.

Collected packages are stored in `self.packages`.

* **Parameters:**
  **path** – The path to the Go project root
* **Raises:**
  [**NoLicenseError**](license_mole.errors.md#license_mole.errors.NoLicenseError) – if a package’s metadata has no licensing data

<a id="license_mole.scan.golang.GoScanner.serialize_cache"></a>

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
