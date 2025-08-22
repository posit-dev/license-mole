<a id="module-license_mole.render"></a>

<a id="license-mole-render-package"></a>

# license_mole.render package

Functions for compiling and rendering notice files.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.render.NoticeRenderer"></a>

### *class* license_mole.render.NoticeRenderer(output: [DocumentDict](license_mole.config_format.md#license_mole.config_format.DocumentDict), groups: list[[RenderGroup](#license_mole.render.RenderGroup)])

Bases: [`LicenseContext`](license_mole.render.context.md#license_mole.render.context.LicenseContext)

A class to render the licensing information for a group of packages.

* **Parameters:**
  * **output** – Description of the document to be generated
  * **groups** – The RenderGroups to be included

<a id="license_mole.render.NoticeRenderer.write"></a>

#### write(path: str)

Render the notice document to disk.

* **Parameters:**
  **path** – The destination path

<a id="license_mole.render.RenderGroup"></a>

### *class* license_mole.render.RenderGroup(group_name: str, packages: list[[BasePackage](license_mole.scan.package.md#license_mole.scan.package.BasePackage)] | list[dict[str, Any]])

Bases: `object`

A description of a functional group of packages.

The name of the group will be used as the interpolation key when rendering
the Markdown template file.

* **Parameters:**
  * **group_name** – The name of the functional group.
  * **packages** – The packages in the group.

<a id="license_mole.render.RenderGroup.render_summary"></a>

#### render_summary(fmt: [FormatDict](license_mole.config_format.md#license_mole.config_format.FormatDict), context: [LicenseContext](license_mole.render.context.md#license_mole.render.context.LicenseContext)) → list[str]

Render the summary for each package in the group.

* **Parameters:**
  * **fmt** – Description of the rendering format
  * **context** – An object containing shared information
* **Returns:**
  A list of Markdown texts

<a id="license_mole.render.RenderGroup.to_dict"></a>

#### to_dict() → list[dict[str, Any]]

Serialize the group.

* **Returns:**
  A dictionary suitable for JSON serialization

* [license_mole.render.context module](license_mole.render.context.md)
  * [`LicenseContext`](license_mole.render.context.md#license_mole.render.context.LicenseContext)
    * [`LicenseContext.excluded`](license_mole.render.context.md#license_mole.render.context.LicenseContext.excluded)
    * [`LicenseContext.format`](license_mole.render.context.md#license_mole.render.context.LicenseContext.format)
    * [`LicenseContext.license_usage`](license_mole.render.context.md#license_mole.render.context.LicenseContext.license_usage)
    * [`LicenseContext.markdown`](license_mole.render.context.md#license_mole.render.context.LicenseContext.markdown)
    * [`LicenseContext.render_license()`](license_mole.render.context.md#license_mole.render.context.LicenseContext.render_license)
    * [`LicenseContext.shared_licenses`](license_mole.render.context.md#license_mole.render.context.LicenseContext.shared_licenses)
* [license_mole.render.labels module](license_mole.render.labels.md)
* [license_mole.render.package module](license_mole.render.package.md)
  * [`RenderPackage`](license_mole.render.package.md#license_mole.render.package.RenderPackage)
    * [`RenderPackage.comparison_key()`](license_mole.render.package.md#license_mole.render.package.RenderPackage.comparison_key)
    * [`RenderPackage.merge()`](license_mole.render.package.md#license_mole.render.package.RenderPackage.merge)
    * [`RenderPackage.render()`](license_mole.render.package.md#license_mole.render.package.RenderPackage.render)
    * [`RenderPackage.render_long()`](license_mole.render.package.md#license_mole.render.package.RenderPackage.render_long)
    * [`RenderPackage.to_dict()`](license_mole.render.package.md#license_mole.render.package.RenderPackage.to_dict)
    * [`RenderPackage.unversioned`](license_mole.render.package.md#license_mole.render.package.RenderPackage.unversioned)
  * [`attribution_comparison_key()`](license_mole.render.package.md#license_mole.render.package.attribution_comparison_key)
  * [`normalize_ltype()`](license_mole.render.package.md#license_mole.render.package.normalize_ltype)
  * [`populate_template()`](license_mole.render.package.md#license_mole.render.package.populate_template)
* [license_mole.render.versiongroup module](license_mole.render.versiongroup.md)
  * [`VersionCompareKey`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionCompareKey)
    * [`VersionCompareKey.attr`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionCompareKey.attr)
    * [`VersionCompareKey.file`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionCompareKey.file)
    * [`VersionCompareKey.ltype`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionCompareKey.ltype)
  * [`VersionGroup`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup)
    * [`VersionGroup.clone()`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.clone)
    * [`VersionGroup.key`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.key)
    * [`VersionGroup.merge()`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.merge)
    * [`VersionGroup.name`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.name)
    * [`VersionGroup.render_long()`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.render_long)
    * [`VersionGroup.render_summary()`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.render_summary)
    * [`VersionGroup.representative`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.representative)
    * [`VersionGroup.sort_key`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.sort_key)
    * [`VersionGroup.url`](license_mole.render.versiongroup.md#license_mole.render.versiongroup.VersionGroup.url)
