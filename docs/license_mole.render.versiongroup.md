<a id="module-license_mole.render.versiongroup"></a>

<a id="license-mole-render-versiongroup-module"></a>

# license_mole.render.versiongroup module

Functions for organizing multiple versions of packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.render.versiongroup.VersionCompareKey"></a>

### *class* license_mole.render.versiongroup.VersionCompareKey

Bases: `TypedDict`

Typing for version comparison keys.

<a id="license_mole.render.versiongroup.VersionCompareKey.attr"></a>

#### attr *: set[str]*

<a id="license_mole.render.versiongroup.VersionCompareKey.file"></a>

#### file *: list[str]*

<a id="license_mole.render.versiongroup.VersionCompareKey.ltype"></a>

#### ltype *: list[str]*

<a id="license_mole.render.versiongroup.VersionGroup"></a>

### *class* license_mole.render.versiongroup.VersionGroup(packages: list[[RenderPackage](license_mole.render.package.md#license_mole.render.package.RenderPackage)])

Bases: `object`

A description of multiple versions of a package.

Versions are grouped based on matching licenses and attribution.

* **Parameters:**
  **packages** – The packages contained within this group
* **Raises:**
  **ValueError** – if the package list is empty

<a id="license_mole.render.versiongroup.VersionGroup.clone"></a>

#### clone(exclude: set[str]) → [VersionGroup](#license_mole.render.versiongroup.VersionGroup) | None

Create a copy of this version group.

* **Parameters:**
  **exclude** – A set of package keys to exclude from the copy
* **Returns:**
  A deep copy of the group referencing the same packages

<a id="license_mole.render.versiongroup.VersionGroup.key"></a>

#### *property* key *: str*

Gets the package key for this group.

<a id="license_mole.render.versiongroup.VersionGroup.merge"></a>

#### merge(other: [VersionGroup](#license_mole.render.versiongroup.VersionGroup), exclude: set[str])

Merge another version group into this one.

* **Parameters:**
  * **other** – Another version group for the same package
  * **exclude** – A set of package keys to ignore

<a id="license_mole.render.versiongroup.VersionGroup.name"></a>

#### *property* name *: str*

Gets the name from a representative package.

<a id="license_mole.render.versiongroup.VersionGroup.render_long"></a>

#### render_long(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), context: [NoticeRenderer](license_mole.render.md#license_mole.render.NoticeRenderer)) → list[str]

Render complete attribution in Markdown for the packages in the group.

* **Parameters:**
  * **fmt** – Description of the rendering format
  * **context** – An object containing shared information
* **Returns:**
  A list of rendered Markdown sections

<a id="license_mole.render.versiongroup.VersionGroup.render_summary"></a>

#### render_summary(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict)) → list[str]

Render a Markdown summary of the packages in the group.

There will be one line for each version group.

* **Parameters:**
  **fmt** – Description of the rendering format
* **Returns:**
  A list of one-line summaries

<a id="license_mole.render.versiongroup.VersionGroup.representative"></a>

#### *property* representative *: [RenderPackage](license_mole.render.package.md#license_mole.render.package.RenderPackage)*

Gets the package that represents the group as a whole.

<a id="license_mole.render.versiongroup.VersionGroup.sort_key"></a>

#### *property* sort_key *: list[str | tuple[int, ...]]*

A key for sorting version groups.

This key will sort first in order of ascending package name, then in
order of descending most recent version.

<a id="license_mole.render.versiongroup.VersionGroup.url"></a>

#### *property* url *: str*

Gets the homepage/repo URL for this group.
