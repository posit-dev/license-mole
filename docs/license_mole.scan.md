# license_mole.scan package

Functions for analyzing and validating license information on packages.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.scan.BaseScanner(name: str)

Bases: `object`

Abstract base class for package scanners.

* **Variables:**
  * **group** – The name of the package group populated by this scanner
  * **packages** – The packages collected by this scanner
  * **cache_data** – Data loaded from the cache, to be used to ensure stable
    results across runs
  * **package_type** – A descriptive label for the type of packages found by
    this scanner
* **Parameters:**
  **name** – The name for a group of packages

#### cache_data *: dict[str, Any]*

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

The default implementation returns False.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Path selectors to current state
* **Returns:**
  True if the cached data is up-to-date

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

If cached data is present, this function will be called even if the
compare_cache function returns False and even if a complete scan
is forced. Implementations may use this information to ensure stable
outputs across runs.

The default implementation does nothing.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

#### group *: str*

#### package_type *= ''*

#### packages *: dict[str, [BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)]*

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan for dependencies for a specified project.

Implementations should store their findings in self.packages.
The definition of a “project root” may vary by scanner.

* **Parameters:**
  **path** – A project root directory

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

The definition of the cached data is scanner-specific, but it should
include sufficient data to identify if the current state of the
repository has changed from the cached state.

The default implementation returns None, which disables caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization

### license_mole.scan.check_cache(scanner_class: type[[BaseScanner](#license_mole.scan.BaseScanner)], groups_to_scan: dict[str, list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]]) → bool

Look for package updates that might require rendering.

* **Parameters:**
  * **scanner_class** – Class to be used to scan for dependencies
  * **groups_to_scan** – Mapping from group names to path globs
* **Returns:**
  True if the cache is up-to-date

### license_mole.scan.detect_licenses(pkgs: list[[BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)]) → list[[BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)]

Run analysis passes to detect licensing information for packages.

* **Parameters:**
  **pkgs** – Packages to analyze
* **Returns:**
  Packages that could not be fully resolved

### license_mole.scan.get_scanners() → dict[str, type[[BaseScanner](#license_mole.scan.BaseScanner)]]

Late-load the scanner classes into SCANNERS.

* **Returns:**
  The scanner dictionary

### license_mole.scan.scan_groups(scanner_class: type[[BaseScanner](#license_mole.scan.BaseScanner)], groups_to_scan: dict[str, list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]], force: bool = False) → dict[str, dict[str, [BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)]]

Search a set of paths for packages and their dependencies.

* **Parameters:**
  * **scanner_class** – Class to be used to recursively load dependencies
    which stores the packages it finds in its .packages property
  * **groups_to_scan** – Mapping from group names to path globs
  * **force** – If True, scan even if the cache is up to date
* **Returns:**
  A dictionary of package groups. Each package group is a dictionary
  mapping package identifiers to a descriptor object.

### license_mole.scan.validate_licenses(pkgs: list[[BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)])

Validate the licensing on a list of packages and log problems.

* **Parameters:**
  **pkgs** – Packages to validate
* **Raises:**
  [**LicenseValidationError**](license_mole.errors.md#license_mole.errors.LicenseValidationError) – if any packages failed validation

* [license_mole.scan.golang module](license_mole.scan.golang.md)
  * [`GoModule`](license_mole.scan.golang.md#license_mole.scan.golang.GoModule)
  * [`GoPackage`](license_mole.scan.golang.md#license_mole.scan.golang.GoPackage)
    * [`GoPackage.key`](license_mole.scan.golang.md#license_mole.scan.golang.GoPackage.key)
    * [`GoPackage.package_type`](license_mole.scan.golang.md#license_mole.scan.golang.GoPackage.package_type)
    * [`GoPackage.serialize()`](license_mole.scan.golang.md#license_mole.scan.golang.GoPackage.serialize)
    * [`GoPackage.url`](license_mole.scan.golang.md#license_mole.scan.golang.GoPackage.url)
  * [`GoScanner`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner)
    * [`GoScanner.compare_cache()`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner.compare_cache)
    * [`GoScanner.deserialize_cache()`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner.deserialize_cache)
    * [`GoScanner.package_type`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner.package_type)
    * [`GoScanner.scan()`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner.scan)
    * [`GoScanner.serialize_cache()`](license_mole.scan.golang.md#license_mole.scan.golang.GoScanner.serialize_cache)
* [license_mole.scan.manual module](license_mole.scan.manual.md)
  * [`ManualPackage`](license_mole.scan.manual.md#license_mole.scan.manual.ManualPackage)
    * [`ManualPackage.key`](license_mole.scan.manual.md#license_mole.scan.manual.ManualPackage.key)
    * [`ManualPackage.package_type`](license_mole.scan.manual.md#license_mole.scan.manual.ManualPackage.package_type)
    * [`ManualPackage.serialize()`](license_mole.scan.manual.md#license_mole.scan.manual.ManualPackage.serialize)
    * [`ManualPackage.url`](license_mole.scan.manual.md#license_mole.scan.manual.ManualPackage.url)
  * [`ManualScanner`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner)
    * [`ManualScanner.compare_cache()`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner.compare_cache)
    * [`ManualScanner.deserialize_cache()`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner.deserialize_cache)
    * [`ManualScanner.package_type`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner.package_type)
    * [`ManualScanner.scan()`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner.scan)
    * [`ManualScanner.serialize_cache()`](license_mole.scan.manual.md#license_mole.scan.manual.ManualScanner.serialize_cache)
* [license_mole.scan.npm module](license_mole.scan.npm.md)
  * [`NpmPackage`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage)
    * [`NpmPackage.dependencies`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.dependencies)
    * [`NpmPackage.key`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.key)
    * [`NpmPackage.package_type`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.package_type)
    * [`NpmPackage.serialize()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.serialize)
    * [`NpmPackage.url`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.url)
    * [`NpmPackage.workspaces`](license_mole.scan.npm.md#license_mole.scan.npm.NpmPackage.workspaces)
  * [`NpmScanner`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner)
    * [`NpmScanner.collect_deps()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.collect_deps)
    * [`NpmScanner.compare_cache()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.compare_cache)
    * [`NpmScanner.deserialize_cache()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.deserialize_cache)
    * [`NpmScanner.package_type`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.package_type)
    * [`NpmScanner.scan()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.scan)
    * [`NpmScanner.serialize_cache()`](license_mole.scan.npm.md#license_mole.scan.npm.NpmScanner.serialize_cache)
* [license_mole.scan.package module](license_mole.scan.package.md)
  * [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)
    * [`BasePackage.deserialize()`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.deserialize)
    * [`BasePackage.ignored`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.ignored)
    * [`BasePackage.key`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.key)
    * [`BasePackage.licenses`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.licenses)
    * [`BasePackage.name`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.name)
    * [`BasePackage.path`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.path)
    * [`BasePackage.serialize()`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.serialize)
    * [`BasePackage.url`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.url)
    * [`BasePackage.version`](license_mole.scan.package.md#license_mole.scan.package.BasePackage.version)
* [license_mole.scan.rust module](license_mole.scan.rust.md)
  * [`PackageGroupConflictError`](license_mole.scan.rust.md#license_mole.scan.rust.PackageGroupConflictError)
  * [`RustBasicPackage`](license_mole.scan.rust.md#license_mole.scan.rust.RustBasicPackage)
    * [`RustBasicPackage.combine_key`](license_mole.scan.rust.md#license_mole.scan.rust.RustBasicPackage.combine_key)
  * [`RustPackage`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage)
    * [`RustPackage.key`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage.key)
    * [`RustPackage.merge()`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage.merge)
    * [`RustPackage.package_type`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage.package_type)
    * [`RustPackage.serialize()`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage.serialize)
    * [`RustPackage.url`](license_mole.scan.rust.md#license_mole.scan.rust.RustPackage.url)
  * [`RustScanner`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner)
    * [`RustScanner.compare_cache()`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner.compare_cache)
    * [`RustScanner.deserialize_cache()`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner.deserialize_cache)
    * [`RustScanner.package_type`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner.package_type)
    * [`RustScanner.scan()`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner.scan)
    * [`RustScanner.serialize_cache()`](license_mole.scan.rust.md#license_mole.scan.rust.RustScanner.serialize_cache)
