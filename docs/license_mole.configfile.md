# license_mole.configfile module

Recursive configuration file handling.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.configfile.ConfigFile(path: str | None, data: dict[str, Any] | None = None)

Bases: `object`

Wrapper around a recursive dictionary.

#### group(key: str) → [ConfigFile](#license_mole.configfile.ConfigFile)

Return a child group from the config file.

If a requested sub-dictionary is found to be a string, it is treated as a
path relative to the current config file, and the contents of that file are
used instead.

If the key does not exist, an empty [`ConfigFile`](#license_mole.configfile.ConfigFile) is returned.

* **Parameters:**
  **key** – Dictionary key.
* **Returns:**
  The contents of the named group.

#### keys() → KeysView[str]

Return the list of keys in the current group.

* **Returns:**
  The list of keys

#### relative_path(path: str) → str

Construct an absolute path to a file relative to this one.

If the path is absolute, it is returned unmodified.

* **Parameters:**
  **path** – The relative path to resolve
* **Returns:**
  An absolute path

#### required_group(key: str) → [ConfigFile](#license_mole.configfile.ConfigFile)

Return a required child group from the config file.

Uses the same behavior as [`group()`](#license_mole.configfile.ConfigFile.group), but raises an exception if
the group is not defined.

* **Parameters:**
  **key** – Dictionary key.
* **Raises:**
  **KeyError** – if the key is not defined.
* **Returns:**
  The contents of the named group.

#### value(key: str, default: Any = None) → Any

Return a value from the config file.

* **Parameters:**
  * **key** – Dictionary key.
  * **default** – If the key is not found, this is returned instead.
* **Returns:**
  The data that was stored in the dictionary.
