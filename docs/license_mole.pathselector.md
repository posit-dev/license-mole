<a id="module-license_mole.pathselector"></a>

<a id="license-mole-pathselector-module"></a>

# license_mole.pathselector module

A class to refer to files across a set of repositories.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.pathselector.NULLPATH"></a>

### license_mole.pathselector.NULLPATH *= ('', 'null://')*

A special PathSelector that uniquely represents the absence of a file.

<a id="license_mole.pathselector.PathSelector"></a>

### *class* license_mole.pathselector.PathSelector(repo: str, path: str)

Bases: `NamedTuple`

A resolved group root selector.

<a id="license_mole.pathselector.PathSelector.parse"></a>

#### *static* parse(value: str | Iterable[str]) → [PathSelector](#license_mole.pathselector.PathSelector)

Parse a value (perhaps from a config file) into a PathSelector.

* **Parameters:**
  **value** – A serialized representation of a path selector
* **Raises:**
  **TypeError** – if the value cannot be converted to a PathSelector
* **Returns:**
  The path selector

<a id="license_mole.pathselector.PathSelector.path"></a>

#### path *: str*

The absolute path to the selected path in the repository.

<a id="license_mole.pathselector.PathSelector.repo"></a>

#### repo *: str*

The environment variable used to find the repository.

There are three special cases:

* `''`: An empty string refers to the root project repository.
* `@`: Refers to a file contained within an installed package.
* [`RUST_VENDOR`](license_mole.config.md#license_mole.config.RUST_VENDOR): Refers to a file contained within the Rust package cache.

<a id="license_mole.pathselector.PathSelector.simplified"></a>

#### *property* simplified *: str | list[str]*

A simplified form of the selector.

Paths in the default repo are returned as a string.
Paths in an alternate repo are returned as a list.

<a id="license_mole.pathselector.PathSelector.to_absolute"></a>

#### to_absolute(path: str = '.') → str

Return the absolute path to a file in the repository.

If the input is a URL or not a relative path, it is returned unchanged.
Paths are interpreted relative to the selected path.

* **Parameters:**
  **path** – A path relative to the selected path
* **Raises:**
  **ValueError** – if this selector is a URL
* **Returns:**
  An absolute path

<a id="license_mole.pathselector.PathSelector.to_relative"></a>

#### to_relative(path: str) → str

Return the relative path to a file in the repository.

If the input is a URL or not an absolute path, it is returned unchanged.
The returned paths is relative to the repository root.

* **Parameters:**
  **path** – An absolute path
* **Returns:**
  A relative path

<a id="license_mole.pathselector.PathSelector.to_selector"></a>

#### to_selector(path: str) → [PathSelector](#license_mole.pathselector.PathSelector)

Return a new PathSelector for another path in the same repository.

Paths are interpreted relative to the repository root.

* **Parameters:**
  **path** – An absolute path, relative path, or URL
* **Returns:**
  A selector for that path
