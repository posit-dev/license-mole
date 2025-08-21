# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for managing license-mole's cache files.

Copyright (c) 2025 Posit Software, PBC
"""

import hashlib
import json
import os
import re
from base64 import standard_b64decode
from datetime import datetime
from typing import Any, Generic, ItemsView, Optional, TypeVar, cast

import requests

from . import DOMAIN_BLACKLIST, logger

T = TypeVar('T')
_CLEAN_URL = re.compile(r'[^A-Za-z0-9]+')
_WEB_CACHE = ''
_RUST_CACHE = ''
_FIREFOX_VERSION = 134 + (datetime.now().year - 2025) * 12 + datetime.now().month
USER_AGENT = f'Mozilla/5.0 (X11; Linux x86_64; rv:{_FIREFOX_VERSION}.0) Gecko/20100101 Firefox/{_FIREFOX_VERSION}.0'


def set_web_cache_root(path: str):
   """Set the web cache root to the specified path.

   If the directory does not exist, it is created.

   :params path: The directory containing the web cache
   """
   global _WEB_CACHE  # noqa: PLW0603
   _WEB_CACHE = path
   os.makedirs(_WEB_CACHE, exist_ok=True)


def download_file_cached(url: str, verbatim: bool = False, headers: Optional[dict[str, str]] = None) -> str:
   """Download a text file from a URL or from a cache on disk.

   The file is assumed to be in UTF-8, and this function will raise an
   exception if it is not.

   The cache is stored in scripts/collect_utils/web_cache. It is never
   automatically invalidated, but it can be manually cleared.

   Special cases:

   * Gitile repositories like googlesource are detected based on the presence
     of "/+/" in the URL. These repositories deliver file downloads in base64
     encoding and require a query string parameter.

   * GitHub repositories will only give clean file downloads with the "/raw/"
     path. If "/tree/" is found it will be replaced with "/raw/". If "/raw/"
     is not found, this function throws an exception.

   :param url: The URL to the file to be downloaded
   :param verbatim: If True, override the usual special-case handling
   :param headers: If set, adds headers to the HTTP request
   :raises ValueError: if the URL is not acceptable or the downloaded file
      is not UTF-8
   :return: The content of the requested file
   """
   if not verbatim:
      for domain in DOMAIN_BLACKLIST:
         if domain in url:
            return ''
      if '//github.com' in url:
         # Special case: only allow /raw/ URLs on GitHub
         url = url.replace('/tree/', '/raw/')
         if '/raw/' not in url:
            raise ValueError(f'Invalid GitHub URL requested: {url}')
      if '/+/' in url and '?' not in url:
         # Special case: Gitile repos download files in base64 with a query string
         url += '?format=TEXT'
   cs = hashlib.sha256(url.encode()).hexdigest()
   slug = _CLEAN_URL.sub('_', '_'.join(url.split('://')[1].split('/')[:3]))
   cache_file = os.path.join(_WEB_CACHE, f'{slug}_{cs}')
   if os.path.exists(cache_file):
      logger.debug('Retrieving %s from cache %s...', url, cs)
      with open(cache_file, 'r', encoding='utf8') as f:
         return f.read()
   logger.debug('Downloading %s to %s...', url, cs)
   response = requests.get(
      url,
      timeout=15.0,
      allow_redirects=True,
      headers={
         'User-Agent': USER_AGENT,
         **(headers or {}),
      },
   )
   if response.status_code == requests.codes['ok']:
      if '/+/' in url:
         text = standard_b64decode(response.content).decode()
      else:
         text = response.content.decode()
   else:
      text = ''
   with open(cache_file, 'w', encoding='utf8') as f:
      f.write(text)
   return text


class BaseCache(Generic[T]):
   """A base class for managing cache files.

   The generic parameter is the type of data stored in a cache entry.

   :ivar auto_save: If True, save the cache to disk on every update
   """

   def __init__(self):
      self.cache_path = ''
      self._cache: dict[str, T] = {}
      self._hashes: dict[str, int] = {}
      self.auto_save = True

   def load(self, path: str):
      """Load the cache from disk.

      :param path: Path to the cache file
      """
      try:
         self.cache_path = path
         with open(path, 'rb') as f:
            self._cache = json.load(f)
      except FileNotFoundError:
         logger.debug(f'Cache file {path} not found, skipping.')
      except json.JSONDecodeError:
         logger.warning(f'Cache file {path} could not be decoded. Ignoring.')

   def save(self):
      """Update the cache on disk."""
      sorted_cache = dict(sorted(self._cache.items()))
      try:
         with open(self.cache_path + '.tmp', 'w', encoding='utf8') as f:
            json.dump(sorted_cache, f, indent=' ')
         os.replace(self.cache_path + '.tmp', self.cache_path)
      except Exception:
         try:
            os.unlink(self.cache_path + '.tmp')
         except FileNotFoundError:
            pass
         raise
      self._clean = True

   def get(self, key: str, default: Optional[T] = None) -> T:
      """Retrieve a value from the cache.

      :param key: The key to the cached data
      :param default: The default value to return if not cached
      :return: The cached data
      """
      if default is None:
         default = cast('T', {})
      return self._cache.get(key, default)

   def set(self, key: str, value: T):
      """Update the cache with new data.

      :param key: The key to the cached data
      :param value: JSON-serializable data
      """
      current = self._hashes.get(key, None)
      value_hash = hash(repr(value))
      if current != value_hash:
         self._hashes[key] = value_hash
         self._cache[key] = value
         if self.auto_save:
            self.save()

   def __contains__(self, key: str) -> bool:
      return key in self._cache

   def items(self) -> ItemsView[str, T]:
      """Return an iterator over the cached items."""
      return self._cache.items()


class ScanCache(BaseCache[dict[str, dict[str, Any]]]):
   """A class to manage the scan cache.

   The scan cache file should be revision-controlled.

   The cache is keyed by package type.
   Cache values are a dict keyed by package key with type-defined values.
   """

   def set(self, package_type: str, group: str, data: dict[str, Any]):  # type: ignore[override]
      """Update the scan cache for a group of packages.

      :param package_type: The type of packages in the group
      :param group: The name of the group
      :param data: Arbitrary JSON-serializable data
      """
      cache_pkg = super().get(package_type, {})
      cache_pkg[group] = data
      super().set(package_type, cache_pkg)

   def get(self, package_type: str, group: str) -> dict[str, Any]:  # type: ignore[override]
      """Fetch cached data for a package group.

      :param package_type: The type of packages in the group
      :param group: The name of the group
      :return: Arbitrary JSON-serializable data
      """
      cache_pkg = super().get(package_type, {})
      return cache_pkg.get(group, {})


scan_cache = ScanCache()
repo_cache = BaseCache[str]()
license_cache = BaseCache[list[dict[str, Any]]]()
license_cache.auto_save = False
