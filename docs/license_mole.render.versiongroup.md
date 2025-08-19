# license_mole.render.versiongroup module

Functions for organizing multiple versions of packages.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.render.versiongroup.VersionCompareKey

Bases: `TypedDict`

Typing for version comparison keys.

#### attr *: set[str]*

#### file *: list[str]*

#### ltype *: list[str]*

### *class* license_mole.render.versiongroup.VersionGroup(packages: list[[RenderPackage](license_mole.render.package.md#license_mole.render.package.RenderPackage)])

Bases: `object`

A description of multiple versions of a package.

Versions are grouped based on matching licenses and attribution.

* **Parameters:**
  **packages** – The packages contained within this group

#### clone(exclude: set[str]) → [VersionGroup](#license_mole.render.versiongroup.VersionGroup)

Create a copy of this version group.

* **Parameters:**
  **exclude** – A set of package keys to exclude from the copy
* **Returns:**
  A deep copy of the group referencing the same packages

#### *property* key *: str*

Gets the package key for this group.

#### merge(other: [VersionGroup](#license_mole.render.versiongroup.VersionGroup), exclude: set[str])

Merge another version group into this one.

* **Parameters:**
  * **other** – Another version group for the same package
  * **exclude** – A set of package keys to ignore

#### *property* name *: str*

Gets the name from a representative package.

#### render_long(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), context: [NoticeRenderer](license_mole.render.md#license_mole.render.NoticeRenderer)) → list[str]

Render complete attribution in Markdown for the packages in the group.

* **Parameters:**
  * **fmt** – Description of the rendering format
  * **context** – An object containing shared information
* **Returns:**
  A list of rendered Markdown sections

#### render_summary(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict)) → list[str]

Render a Markdown summary of the packages in the group.

There will be one line for each version group.

* **Parameters:**
  **fmt** – Description of the rendering format
* **Returns:**
  A list of one-line summaries

#### *property* representative *: [RenderPackage](license_mole.render.package.md#license_mole.render.package.RenderPackage)*

Gets the package that represents the group as a whole.

#### *property* url *: str*

Gets the homepage/repo URL for this group.
