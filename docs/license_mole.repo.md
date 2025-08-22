<a id="module-license_mole.repo"></a>

<a id="license-mole-repo-module"></a>

# license_mole.repo module

Functions for finding source code repositories for packages.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.repo.clean_repo_url"></a>

### license_mole.repo.clean_repo_url(url: str) → str

Resolve a repository URL string to a proper, working HTTP(S) URL.

npm does not require a standardized format for repository URLs inside
package.json and several variations have been seen in the wild.

Go packages are usually named after their source code repository, but
it’s not entirely consistent.

If the input URL is not cached, this function attempts to fetch the URL.
If the URL is redirected, then the redirected URL is used instead. The
cleaned, tested URL is saved to the cache. If the request fails or returns
an error, this function returns an empty string and it is not cached.

* **Parameters:**
  **url** – Unresolved repository URL from package metadata
* **Returns:**
  Resolved repository URL

<a id="license_mole.repo.find_file_in_repo"></a>

### license_mole.repo.find_file_in_repo(repo_url: str, path: str) → str

Resolve the URL for a file at a path within a git repository.

For GitHub repos, the file is downloaded to verify its presence.
A subsequent call to `download_file_cached` is guaranteed to read
from the cache. For non-GitHub repos, the file is not downloaded.

* **Parameters:**
  * **repo_url** – The repository URL
  * **path** – The file’s path within the repository
* **Returns:**
  The resolved file URL, or an empty string if not found

<a id="license_mole.repo.get_github_branch"></a>

### license_mole.repo.get_github_branch(repo_url: str) → str

Identify the primary branch for a GitHub repo.

The repo URL should have been cleaned with [`clean_repo_url`](#license_mole.repo.clean_repo_url).
If a non-GitHub URL is provided, defaults to “master”.

* **Parameters:**
  **repo_url** – The GitHub repository URL
* **Returns:**
  The name of the primary branch (e.g. master, main)
