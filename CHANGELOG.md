# CHANGELOG


## v0.3.0 (2025-12-15)

### Bug Fixes

- Ensure summaries use the same anchors as long descriptions
  ([`9c9a1a1`](https://github.com/posit-dev/license-mole/commit/9c9a1a1a62894980606178402325561070312dd3))

- Handle Markdown links with <> brackets
  ([`54480d6`](https://github.com/posit-dev/license-mole/commit/54480d6c0b2225f8f14ff732f6ac252ccffdc796))

- Label links as 'Source' instead of 'Website' for accuracy
  ([`7cacb61`](https://github.com/posit-dev/license-mole/commit/7cacb610f99220dd9124038de4134298f765222e))

### Features

- Generate web URLs for repo-relative paths
  ([`75cea75`](https://github.com/posit-dev/license-mole/commit/75cea75d853d6ee750f5c6d897070a8e908dcde8))


## v0.2.2 (2025-12-12)

### Bug Fixes

- Multi-license files skipped undefined names, add HPND
  ([`c14a0b0`](https://github.com/posit-dev/license-mole/commit/c14a0b0fd153150394e854206eda91f2ded25d6d))

- Multi-license links, anchors to package groups
  ([`de3cd34`](https://github.com/posit-dev/license-mole/commit/de3cd349f1ba92fe100b9478919383a8bc686415))


## v0.2.1 (2025-09-08)

### Bug Fixes

- Add PSF-2.0
  ([`3fa6630`](https://github.com/posit-dev/license-mole/commit/3fa6630f1f583766b6088711e0c6fd607f9b15cc))


## v0.2.0 (2025-09-05)

### Bug Fixes

- Add missing ~= operator in Python atoms
  ([`46f58c3`](https://github.com/posit-dev/license-mole/commit/46f58c37e8ad6cdd40a214177da86acf1fad4365))

- Correct broken logic in exclude feature
  ([`ed67e73`](https://github.com/posit-dev/license-mole/commit/ed67e735ed5494b1ec3b25dedb496311d9ac1b2d))

- Deal with invalid `project_urls`, skip ambiguous identifiers
  ([`803e60a`](https://github.com/posit-dev/license-mole/commit/803e60ab680726256fb353de5f415bd98e7495b4))

- Handle Python deps without version numbers
  ([`0c66453`](https://github.com/posit-dev/license-mole/commit/0c66453f6b5041cea4f8ca1041ed6e22a295540d))

- Honor license overrides for Python deps
  ([`a962d99`](https://github.com/posit-dev/license-mole/commit/a962d9998a7d9dcf7cff966e4ebf86749f25bf5e))

- Remove references to obsolete paths
  ([`bfd5290`](https://github.com/posit-dev/license-mole/commit/bfd5290ea151c623f3536244150b4e21374d464b))

### Documentation

- Replace ivar with attribute docs, regenerate apidoc
  ([`3f0e2c5`](https://github.com/posit-dev/license-mole/commit/3f0e2c5fc3a9227e20f6a09811604b6e2e676a4f))

### Features

- Support Rust group configuration without hardcoding
  ([`23a4563`](https://github.com/posit-dev/license-mole/commit/23a4563329f9890b28b340031310a20f55c0e597))


## v0.1.0 (2025-08-21)

### Bug Fixes

- Apache license, Elastic license detection, URL ltypes
  ([`3d1a19d`](https://github.com/posit-dev/license-mole/commit/3d1a19dcd946c61906ca54ea1ed859e1d0526248))

- Correct git hooks installation
  ([`5988df8`](https://github.com/posit-dev/license-mole/commit/5988df8f7e18435107500a9691fff0711cd37552))

- Fix version sorting and merging
  ([`5a1ae10`](https://github.com/posit-dev/license-mole/commit/5a1ae1080753a393a21fe87bedb200f7dfbcc0db))

- Handle bidirectional group merging
  ([`b05bf98`](https://github.com/posit-dev/license-mole/commit/b05bf98057b6397504eab9bebec8f7c7c7a8c02d))

- Improve "clean" license detection, make sure to output
  ([`ede4db7`](https://github.com/posit-dev/license-mole/commit/ede4db72e81eceb425112f0a24b7e3f20c982a1c))

- Make anchor hashing stable
  ([`579fc25`](https://github.com/posit-dev/license-mole/commit/579fc2508345365ad8f05f05c28f1f1abb1facee))

- Markdown blockquote rendering, support specifying package.json explicitly
  ([`60a48da`](https://github.com/posit-dev/license-mole/commit/60a48daa87d362abc253827976b459b8f6a72fdc))

- Npm nls displayName, more standard license support
  ([`e14844b`](https://github.com/posit-dev/license-mole/commit/e14844bee0e77f3bc3b994d2e7a017ce990cdef6))

- Various npm fixes, deal with URLs in license types
  ([`65b3ab0`](https://github.com/posit-dev/license-mole/commit/65b3ab0af06b93caa36386db106ef825b4dc3712))

### Chores

- Add Makefile rules for PSR, improve npm path detection
  ([`cf47491`](https://github.com/posit-dev/license-mole/commit/cf47491e2b86fa188fdb47fcf610488826b83cb7))

- Add PSR
  ([`d98a2b4`](https://github.com/posit-dev/license-mole/commit/d98a2b4b4938fb642ffe9560411ecbcb68acb53b))

- Set up linting, regenerate docs
  ([`a8fb020`](https://github.com/posit-dev/license-mole/commit/a8fb02091f5e6de81ebc745a0fcd63e48097555c))

### Features

- Add Python (Poetry) support, bootstrap own license file
  ([`f7be4a3`](https://github.com/posit-dev/license-mole/commit/f7be4a33493a767cb758aabe58c7c5fd88bd2540))

- Support PathSelectors in overrides
  ([`28e5bb0`](https://github.com/posit-dev/license-mole/commit/28e5bb0ba370a43eff99f9de9be2140992439a00))
