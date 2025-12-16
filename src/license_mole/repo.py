# vim: ts=3 sts=3 sw=3 expandtab:
"""Functions for finding source code repositories for packages.

Copyright (c) 2025 Posit Software, PBC
SPDX-License-Identifier: MIT
"""

import json
import os
import re
import subprocess
from functools import cache

import requests

from . import logger
from .cache import download_file_cached, repo_cache

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_PATTERN = re.compile(r'^[\w.-]+/[\w.-]+$')
COMMON_BRANCHES = ['main', 'master', 'trunk']
URL_REPLACEMENTS = {
   'git+': '',
   'git://github.com/': 'https://github.com/',
   'git@github.com:': 'https://github.com/',
   'github:': 'https://github.com/',
   'ssh://git@github.com/': 'https://github.com/',
   'http://github.com/': 'https://github.com/',
   'github.com/': 'https://github.com/',
   'golang.org/': 'https://pkg.go.dev/golang.org/',
   'gopkg.in/': 'https://gopkg.in/',
}


@cache
def clean_repo_url(url: str) -> str:
   """Resolve a repository URL string to a proper, working HTTP(S) URL.

   npm does not require a standardized format for repository URLs inside
   package.json and several variations have been seen in the wild.

   Go packages are usually named after their source code repository, but
   it's not entirely consistent.

   If the input URL is not cached, this function attempts to fetch the URL.
   If the URL is redirected, then the redirected URL is used instead. The
   cleaned, tested URL is saved to the cache. If the request fails or returns
   an error, this function returns an empty string and it is not cached.

   :param url: Unresolved repository URL from package metadata
   :return: Resolved repository URL
   """
   if not url:
      return ''
   if url in repo_cache:
      return repo_cache.get(url) or ''
   for prefix, replacement in URL_REPLACEMENTS.items():
      if url.startswith(prefix):
         url = url.replace(prefix, replacement)
   if REPO_PATTERN.match(url):
      gh_url = f'https://github.com/{url}'
      logger.debug('Checking %s', gh_url)
      response = requests.head(gh_url, timeout=15.0)
      if response.is_redirect:
         gh_url = response.headers['Location']
      if response.is_redirect or response.status_code == requests.codes['ok']:
         repo_cache.set(url, gh_url)
         url = gh_url
   if not url.startswith('https://') and not url.startswith('http://'):
      # Couldn't resolve the URL to something usable
      return ''
   if url.startswith('https://github.com') and '/tree/' in url:
      url = url.split('/tree/')[0]
   if url.startswith('https://github.com') and url.endswith('.git'):
      url = url[:-4]
   return url


def _guess_github_branch(org: str, repo: str) -> str:
   """Guess the primary branch for a GitHub repo.

   This is a fallback used when the repo can't be found using the orgs API.

   :param org: The name of the owner of the repo
   :param repo: The name of the repo
   :raises RuntimeError: if a branch cannot be identified
   :return: The name of the primary branch (e.g. master, main)
   """
   base_url = f'https://api.github.com/repos/{org}/{repo}/branches?per_page=100&page=%d&protected=%s'
   for protected in ['true', 'false']:
      page = 0
      while True:
         page += 1
         response = download_file_cached(base_url % (page, protected))
         if not response:
            # Can't access the API
            break
         repo_data = json.loads(response)
         branches = [b['name'] for b in repo_data]
         if not branches:
            break
         for branch in COMMON_BRANCHES:
            if branch in branches:
               return branch
   # If the API is unavailable, try just basic requests
   base_url = f'https://github.com/{org}/{repo}/tree/%s'
   for branch in COMMON_BRANCHES:
      response = download_file_cached(base_url % (branch,), verbatim=True)
      if response:
         return branch
   raise RuntimeError(f'Could not find primary branch for {org}/{repo}')


def get_github_branch(repo_url: str) -> str:
   """Identify the primary branch for a GitHub repo.

   The repo URL should have been cleaned with `clean_repo_url`.
   If a non-GitHub URL is provided, defaults to "master".

   :param repo_url: The GitHub repository URL
   :return: The name of the primary branch (e.g. master, main)
   """
   if '//github.com/' not in repo_url:
      return 'master'

   org, repo = repo_url.split('/')[3:5]

   # special case
   if org == 'rstudio' and repo == 'rstudio-pro':
      return subprocess.run(['git', 'branch', '--show-current'], check=True, stdout=subprocess.PIPE).stdout.strip().decode()

   response = download_file_cached(f'https://api.github.com/orgs/{org}/repos?per_page=100')
   if not response:
      # Not an organization, so orgs API doesn't work
      return _guess_github_branch(org, repo)
   try:
      repo_data = next(r for r in json.loads(response) if r['name'] == repo)
      return repo_data['default_branch']
   except StopIteration:
      # The repo wasn't found using the orgs API
      return _guess_github_branch(org, repo)


def find_file_in_repo(repo_url: str, path: str) -> str:
   """Resolve the URL for a file at a path within a git repository.

   For GitHub repos, the file is downloaded to verify its presence.
   A subsequent call to `download_file_cached` is guaranteed to read
   from the cache. For non-GitHub repos, the file is not downloaded.

   :param repo_url: The repository URL
   :param path: The file's path within the repository
   :return: The resolved file URL, or an empty string if not found
   """
   if not repo_url or not path:
      return ''
   path = path.strip('/')
   if repo_url.startswith('https://github.com'):
      repo_url = repo_url.replace('/tree/', '/raw/')
      if '/raw/' in repo_url:
         branch = repo_url.split('/raw/')[1].split('/')[0]
      else:
         branch = get_github_branch(repo_url)
      # if type(branch) is not str:
      #    raise TypeError('how did we get here '+repr(repo_url))
      root = '/'.join(repo_url.split('/')[:5])
      resolved_url = f'{root}/raw/{branch}/{path}'
      if download_file_cached(resolved_url):
         return resolved_url
      return ''
   return f'{repo_url}/{path}'
