# license_mole.scan.npm module

Functions for collecting npm packages.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.scan.npm.NpmPackage(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of an npm package.

The constructor loads package.json and collects relevant information.

* **Variables:**
  **package_json** – The parsed contents of package.json
* **Parameters:**
  **path** – Path to the directory containing package.json
* **Raises:**
  [**MissingPackageError**](license_mole.errors.md#license_mole.errors.MissingPackageError) – if package.json cannot be loaded

#### *property* dependencies *: list[str]*

The list of direct dependencies, as npm version atoms.

#### *property* key *: str*

A unique key identifying the package.

#### package_type *= 'NPM'*

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

#### *property* url *: str*

The URL to a “homepage” for the package.

#### *property* workspaces *: list[str]*

The list of workspaces found in package.json.

### *class* license_mole.scan.npm.NpmScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects npm packages and their dependencies.

#### collect_deps(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Load package.json and scan child dependencies.

This function will skip packages that have already been loaded.

* **Parameters:**
  **path** – Path to the directory containing package.json
* **Raises:**
  [**NoLicenseError**](license_mole.errors.md#license_mole.errors.NoLicenseError) – if the package has no license information

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

#### package_type *= 'NPM'*

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Entry point for scanning a package tree.

* **Parameters:**
  **path** – The root of the package tree

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
