<a id="module-license_mole.config"></a>

<a id="license-mole-config-module"></a>

# license_mole.config module

Project configuration information.

Copyright (c) 2025 Posit Software, PBC

All configuration paths are relative to the directory containing mole.toml.

Packages that do not name a repository are located relative to the default
repository path given by the “root” value in mole.toml. If “root” is not
specified, the directory containing mole.toml is also used as the path to
the default repository.

Relative paths to repositories are resolved relative to the directory
containing mole.toml.

<a id="license_mole.config.OverrideDict"></a>

### *class* license_mole.config.OverrideDict

Bases: `TypedDict`

A set of overrides for a package’s metadata.

<a id="license_mole.config.OverrideDict.attribution"></a>

#### attribution *: list[str]*

Copyright lines, ideally with year and author.

<a id="license_mole.config.OverrideDict.author"></a>

#### author *: str*

The author of the package.

<a id="license_mole.config.OverrideDict.ignored"></a>

#### ignored *: bool*

If True, the package is skipped during scanning.

<a id="license_mole.config.OverrideDict.license"></a>

#### license *: tuple[str, ...]*

SPDX-style license identifier(s).

<a id="license_mole.config.OverrideDict.license_files"></a>

#### license_files *: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]*

Absolute paths or URLs to the text of the license.

<a id="license_mole.config.OverrideDict.permit_license_change"></a>

#### permit_license_change *: bool*

If True, this package is allowed to be consolidated into a package with different licensing attribution.

<a id="license_mole.config.OverrideDict.rename"></a>

#### rename *: str*

Replaces the package name to unify renamed versions.

<a id="license_mole.config.OverrideDict.url"></a>

#### url *: str*

The URL for the package source code repository.

<a id="license_mole.config.RUST_VENDOR"></a>

### license_mole.config.RUST_VENDOR *= '\\x00RUST'*

A unique identifier to create `PathSelector` objects that refer to the Rust vendor cache.

<a id="license_mole.config.get_file_overrides"></a>

### license_mole.config.get_file_overrides(path: str) → Literal[False] | tuple[str, ...]

Get a license identifier to override the automatic detection.

* **Parameters:**
  **path** – A path or URL to a license file
* **Returns:**
  License identifier override, if known

<a id="license_mole.config.get_overrides"></a>

### license_mole.config.get_overrides(pkg: str) → [OverrideDict](#license_mole.config.OverrideDict)

Get a dictionary of overrides for a package based on its key.

* **Parameters:**
  **pkg** – Package identifier
* **Returns:**
  Known metadata overrides

<a id="license_mole.config.load_config"></a>

### license_mole.config.load_config(path: str)

Load configuration from a mole.toml file.

* **Parameters:**
  **path** – path to configuration file
