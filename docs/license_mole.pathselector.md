# license_mole.pathselector module

A class to refer to files across a set of repositories.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.pathselector.PathSelector(repo: str, path: str)

Bases: `NamedTuple`

A resolved group root selector.

* **Variables:**
  * **repo** – The environment variable used to find the repository
  * **path** – The absolute path to the selected path in the repository

#### path *: str*

Alias for field number 1

#### repo *: str*

Alias for field number 0

#### *property* simplified *: str | list[str]*

A simplified form of the selector.

Paths in the default repo are returned as a string.
Paths in an alternate repo are returned as a list.

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

#### to_relative(path: str) → str

Return the relative path to a file in the repository.

If the input is a URL or not an absolute path, it is returned unchanged.
The returned paths is relative to the repository root.

* **Parameters:**
  **path** – An absolute path
* **Returns:**
  A relative path

#### to_selector(path: str) → [PathSelector](#license_mole.pathselector.PathSelector)

Return a new PathSelector for another path in the same repository.

Paths are interpreted relative to the repository root.

* **Parameters:**
  **path** – An absolute path, relative path, or URL
* **Returns:**
  A selector for that path
