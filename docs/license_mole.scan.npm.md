<a id="module-license_mole.scan.npm"></a>

<a id="license-mole-scan-npm-module"></a>

# license_mole.scan.npm module

Functions for collecting npm packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.scan.npm.NpmPackage"></a>

### *class* license_mole.scan.npm.NpmPackage(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of an npm package.

The constructor loads package.json and collects relevant information.

* **Parameters:**
  **path** – Path to the directory containing package.json
* **Raises:**
  [**MissingPackageError**](license_mole.errors.md#license_mole.errors.MissingPackageError) – if package.json cannot be loaded

<a id="license_mole.scan.npm.NpmPackage.dependencies"></a>

#### *property* dependencies *: list[str]*

The list of direct dependencies, as npm version atoms.

<a id="license_mole.scan.npm.NpmPackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

<a id="license_mole.scan.npm.NpmPackage.package_json"></a>

#### package_json *: dict[str, Any]*

The parsed contents of `package.json`.

<a id="license_mole.scan.npm.NpmPackage.package_type"></a>

#### package_type *: str* *= 'NPM'*

Label for rendering what kind of package this is.

<a id="license_mole.scan.npm.NpmPackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.npm.NpmPackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

<a id="license_mole.scan.npm.NpmPackage.workspaces"></a>

#### *property* workspaces *: list[str]*

The list of workspaces found in package.json.

<a id="license_mole.scan.npm.NpmScanner"></a>

### *class* license_mole.scan.npm.NpmScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects npm packages and their dependencies.

<a id="license_mole.scan.npm.NpmScanner.collect_deps"></a>

#### collect_deps(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Load package.json and scan child dependencies.

This function will skip packages that have already been loaded.

* **Parameters:**
  **path** – Path to the directory containing package.json
* **Raises:**
  [**NoLicenseError**](license_mole.errors.md#license_mole.errors.NoLicenseError) – if the package has no license information

<a id="license_mole.scan.npm.NpmScanner.compare_cache"></a>

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

<a id="license_mole.scan.npm.NpmScanner.deserialize_cache"></a>

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

<a id="license_mole.scan.npm.NpmScanner.package_type"></a>

#### package_type *= 'NPM'*

A descriptive label for the type of packages found by this scanner.

<a id="license_mole.scan.npm.NpmScanner.scan"></a>

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Entry point for scanning a package tree.

* **Parameters:**
  **path** – The root of the package tree

<a id="license_mole.scan.npm.NpmScanner.serialize_cache"></a>

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
