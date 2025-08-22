<a id="module-license_mole.scan.manual"></a>

<a id="license-mole-scan-manual-module"></a>

# license_mole.scan.manual module

Functions for collecting manual dependency information.

Copyright (c) 2025 Posit Software, PBC

For dependencies that are not managed with a package manager, license-mole
supports a format in the style of a CMake function. A minimal dependency
definition looks like this:

```default
dependency(<IDENTIFIER>
   DEPNAME    "<display-name>"
   REPOSITORY "<url>"
)
```

Text in a dependency file that is outside of a `dependency()` block is
ignored. This allows the use of a `CMakeLists.txt` file containing these
definitions. Comments begin with a `#` character.

The following arguments are supported:

* `<IDENTIFIER>`: *Required.* A unique identifier for this dependency. This
  : identifier should not be quoted and spaces are not allowed. While
    license-mole places no other restrictions on this identifier, it should be a
    valid CMake variable name if CMake is used.
    license-mole places no requirements on this identifier,
* `DEPNAME`: A display name for the dependency, to be rendered in the output.
  : The identifier will be rendered if `DEPNAME` is omitted.
* `PATH`: A path relative to the project root where the dependency’s files
  : are located.
* `REPOSITORY`: An HTTP/HTTPS URL to a git repository where the dependency can
  : be found. This may include a path to a directory inside the repository.
* `HOMEPAGE`: A URL to a webpage where a user can find more information about
  : the dependency. This will be used when rendering the output in preference to
    `REPOSITORY` if both are provided. license-mole will not use this URL to
    collect license information.
* `REVISION`: A `commit-ish` in the repository where the specific version of
  : the dependency is found.
* `VERSION`: A version number for the dependency. This is used for caching and
  : rendering.
* `LICENSE`: An SPDX identifier for the dependency’s license.
* `LICENSE_PATH`: A comma-separated list of URLs or paths to the text of the
  : dependency’s license. Paths are interpreted relative to `REPOSITORY` or
    `PATH`.
* `AUTHOR`: The dependency’s author, maintainer, or packager.
* `ATTRIBUTION`: A line of copyright attribution. If present, `AUTHOR` is
  : ignored.

At least one of `PATH`, `REPOSITORY`, or `HOMEPAGE` is required.
Unrecognized arguments are ignored.

This format may be parsed in your own CMake functions using the
[cmake_parse_arguments](https://cmake.org/cmake/help/latest/command/cmake_parse_arguments.html)
function. A simple example function:

```default
function(dependency)
   set(_NAME "${ARGV0}")
   cmake_parse_arguments(
      PARSE_ARGV 1
      "" ""
      "DEPNAME;PATH;VERSION;REPOSITORY;REVISION;HOMEPAGE;AUTHOR;ATTRIBUTION;LICENSE;LICENSE_PATH"
      ""
   )
   set(${_NAME}_VERSION "${_VERSION}")
   set(${_NAME}_PATH "${_PATH}")
   set(${_NAME}_REPOSITORY "${_REPOSITORY}")
   set(${_NAME}_REVISION "${_REVISION}")
endfunction()
```

<a id="license_mole.scan.manual.ManualPackage"></a>

### *class* license_mole.scan.manual.ManualPackage(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector), pkg: dict[str, str])

Bases: [`BasePackage`](license_mole.scan.package.md#license_mole.scan.package.BasePackage)

A description of a manual package.

* **Parameters:**
  * **selector** – Path selector for the file containing the definition
  * **pkg** – Parsed package information

<a id="license_mole.scan.manual.ManualPackage.key"></a>

#### *property* key *: str*

A unique key identifying the package.

<a id="license_mole.scan.manual.ManualPackage.package_type"></a>

#### package_type *: str* *= ''*

Label for rendering what kind of package this is.

<a id="license_mole.scan.manual.ManualPackage.serialize"></a>

#### serialize(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any]

Serialize the package for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A JSON-compatible dict of package metadata.

<a id="license_mole.scan.manual.ManualPackage.url"></a>

#### *property* url *: str*

The URL to a “homepage” for the package.

<a id="license_mole.scan.manual.ManualScanner"></a>

### *class* license_mole.scan.manual.ManualScanner(group: str)

Bases: [`BaseScanner`](license_mole.scan.md#license_mole.scan.BaseScanner)

A scanner that collects manually-specified dependency information.

<a id="license_mole.scan.manual.ManualScanner.compare_cache"></a>

#### compare_cache(cache: dict[str, Any], paths: list[[PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)]) → bool

Compare cached data to the current state.

If this function returns True, then the cached data is considered to be
up-to-date and the scan does not need to be re-run.

* **Parameters:**
  * **cache** – Data that had been previously saved in the cache
  * **paths** – Absolute paths to current state
* **Returns:**
  True if the cached data is up-to-date

<a id="license_mole.scan.manual.ManualScanner.deserialize_cache"></a>

#### deserialize_cache(cache: dict[str, Any], selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Populate the scanner with cached data.

* **Parameters:**
  * **cache** – The serialized data from the cache
  * **selector** – The selector that paths are relative to

<a id="license_mole.scan.manual.ManualScanner.package_type"></a>

#### package_type *= 'manual'*

A descriptive label for the type of packages found by this scanner.

<a id="license_mole.scan.manual.ManualScanner.scan"></a>

#### scan(path: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector))

Scan a dependency text file for information.

Collected packages are stored in `self.packages`.

* **Parameters:**
  **path** – The path to the dependency text file

<a id="license_mole.scan.manual.ManualScanner.serialize_cache"></a>

#### serialize_cache(selector: [PathSelector](license_mole.pathselector.md#license_mole.pathselector.PathSelector)) → dict[str, Any] | None

Serialize the scan results for caching.

* **Parameters:**
  **selector** – The selector that paths are relative to
* **Returns:**
  A dict suitable for JSON serialization
