# license_mole.scan.python module

Functions for collecting Python packages.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.scan.python.PythonPackage(atom: \_ParsedAtom, lock_version: str | None = None)

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a manual package.

* **Parameters:**
  * **atom** – A version atom that refers to the dependency
  * **lock_version** – The version number from the lockfile

#### *property* key *: str*

A unique key identifying the package.

#### package_type *= 'Python'*

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

#### *property* url *: str*

The URL to a “homepage” for the package.

### *class* license_mole.scan.python.PythonScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects manually-specified dependency information.

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

#### package_type *= 'Python'*

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan a Python project for dependency information.

Collected packages are stored in self.packages.

* **Parameters:**
  **path** – The path to the directory containing pyproject.toml

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
