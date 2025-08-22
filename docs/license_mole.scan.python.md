<a id="module-license_mole.scan.python"></a>

<a id="license-mole-scan-python-module"></a>

# license_mole.scan.python module

Functions for collecting Python packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.scan.python.PythonPackage"></a>

### *class* license_mole.scan.python.PythonPackage(atom: \_ParsedAtom, lock_version: str | None = None)

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a manual package.

* **Parameters:**
  * **atom** – A version atom that refers to the dependency
  * **lock_version** – The version number from the lockfile

<a id="license_mole.scan.python.PythonPackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

<a id="license_mole.scan.python.PythonPackage.package_type"></a>

#### package_type *: str* *= 'Python'*

Label for rendering what kind of package this is.

<a id="license_mole.scan.python.PythonPackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.python.PythonPackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

<a id="license_mole.scan.python.PythonScanner"></a>

### *class* license_mole.scan.python.PythonScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects manually-specified dependency information.

<a id="license_mole.scan.python.PythonScanner.compare_cache"></a>

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

<a id="license_mole.scan.python.PythonScanner.deserialize_cache"></a>

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

<a id="license_mole.scan.python.PythonScanner.package_type"></a>

#### package_type *= 'Python'*

A descriptive label for the type of packages found by this scanner.

<a id="license_mole.scan.python.PythonScanner.scan"></a>

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan a Python project for dependency information.

Collected packages are stored in `self.packages`.

* **Parameters:**
  **path** – The path to the directory containing pyproject.toml

<a id="license_mole.scan.python.PythonScanner.serialize_cache"></a>

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
