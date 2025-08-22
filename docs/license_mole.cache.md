<a id="module-license_mole.cache"></a>

<a id="license-mole-cache-module"></a>

# license_mole.cache module

Functions for managing license-mole’s cache files.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.cache.BaseCache"></a>

### *class* license_mole.cache.BaseCache

Bases: `Generic`[`T`]

A base class for managing cache files.

The generic parameter is the type of data stored in a cache entry.

<a id="license_mole.cache.BaseCache.auto_save"></a>

#### auto_save *: bool*

If True, save the cache to disk on every update

<a id="license_mole.cache.BaseCache.cache_path"></a>

#### cache_path *: str*

The path to the cache on disk.

<a id="license_mole.cache.BaseCache.get"></a>

#### get(key: str, default: T | None = None) → T

Retrieve a value from the cache.

* **Parameters:**
  * **key** – The key to the cached data
  * **default** – The default value to return if not cached
* **Returns:**
  The cached data

<a id="license_mole.cache.BaseCache.items"></a>

#### items() → ItemsView[str, T]

Return an iterator over the cached items.

<a id="license_mole.cache.BaseCache.load"></a>

#### load(path: str)

Load the cache from disk.

* **Parameters:**
  **path** – Path to the cache file

<a id="license_mole.cache.BaseCache.save"></a>

#### save()

Update the cache on disk.

<a id="license_mole.cache.BaseCache.set"></a>

#### set(key: str, value: T)

Update the cache with new data.

* **Parameters:**
  * **key** – The key to the cached data
  * **value** – JSON-serializable data

<a id="license_mole.cache.ScanCache"></a>

### *class* license_mole.cache.ScanCache

Bases: [`BaseCache`](#license_mole.cache.BaseCache)[`dict`[`str`, `dict`[`str`, `Any`]]]

A class to manage the scan cache.

The scan cache file should be revision-controlled.

The cache is keyed by package type.
Cache values are a dict keyed by package key with type-defined values.

<a id="license_mole.cache.ScanCache.get"></a>

#### get(package_type: str, group: str) → dict[str, Any]

Fetch cached data for a package group.

* **Parameters:**
  * **package_type** – The type of packages in the group
  * **group** – The name of the group
* **Returns:**
  Arbitrary JSON-serializable data

<a id="license_mole.cache.ScanCache.set"></a>

#### set(package_type: str, group: str, data: dict[str, Any])

Update the scan cache for a group of packages.

* **Parameters:**
  * **package_type** – The type of packages in the group
  * **group** – The name of the group
  * **data** – Arbitrary JSON-serializable data

<a id="license_mole.cache.download_file_cached"></a>

### license_mole.cache.download_file_cached(url: str, verbatim: bool = False, headers: dict[str, str] | None = None) → str

Download a text file from a URL or from a cache on disk.

The file is assumed to be in UTF-8, and this function will raise an
exception if it is not.

The cache is stored in .mole.web_cache by default, configurable in the
mole.toml file. It is never automatically invalidated, but it can be
manually cleared.

Special cases:

* Gitile repositories like googlesource are detected based on the presence
  of “/+/” in the URL. These repositories deliver file downloads in base64
  encoding and require a query string parameter.
* GitHub repositories will only give clean file downloads with the “/raw/”
  path. If “/tree/” is found it will be replaced with “/raw/”. If “/raw/”
  is not found, this function throws an exception.

* **Parameters:**
  * **url** – The URL to the file to be downloaded
  * **verbatim** – If True, override the usual special-case handling
  * **headers** – If set, adds headers to the HTTP request
* **Raises:**
  **ValueError** – if the URL is not acceptable or the downloaded file
  is not UTF-8
* **Returns:**
  The content of the requested file

<a id="license_mole.cache.set_web_cache_root"></a>

### license_mole.cache.set_web_cache_root(path: str)

Set the web cache root to the specified path.

If the directory does not exist, it is created.

* **Params path:**
  The directory containing the web cache
