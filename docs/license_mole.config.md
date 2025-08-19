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

### *class* license_mole.config.OverrideDict

Bases: `TypedDict`

A set of overrides for a package’s metadata.

#### attribution *: list[str]*

Copyright lines, ideally with year and author.

#### author *: str*

The author of the package.

#### ignored *: bool*

If True, the package is skipped during scanning.

#### license *: tuple[str, ...]*

SPDX-style license identifier(s).

#### license_files *: list[str]*

Absolute paths or URLs to the text of the license.

#### permit_license_change *: bool*

If True, this package is allowed to be consolidated into a package with different licensing attribution.

#### rename *: str*

Replaces the package name to unify renamed versions.

#### url *: str*

The URL for the package source code repository.

### license_mole.config.get_file_overrides(path: str) → Literal[False] | tuple[str, ...]

Get a license identifier to override the automatic detection.

* **Parameters:**
  **path** – A path or URL to a license file
* **Returns:**
  License identifier override, if known

### license_mole.config.get_overrides(pkg: str) → [OverrideDict](#license_mole.config.OverrideDict)

Get a dictionary of overrides for a package based on its key.

* **Parameters:**
  **pkg** – Package identifier
* **Returns:**
  Known metadata overrides

### license_mole.config.load_config(path: str)

Load configuration from a mole.toml file.

* **Parameters:**
  **path** – path to configuration file
