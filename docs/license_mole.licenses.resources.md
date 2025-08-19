# license_mole.licenses.resources package

Access to predefined license text.

Copyright (c) 2025 Posit Software, PBC

### license_mole.licenses.resources.get_standard_license_reference(spdx: str) → str

Produce a URI for the standard text for a license.

* **Parameters:**
  **spdx** – The SPDX identifier of the license.
* **Raises:**
  **FileNotFoundError** – if the license does not have standard text.
* **Returns:**
  A URI for the license.

### license_mole.licenses.resources.get_standard_license_text(spdx: str) → str

Retrieve the standard text for a license.

This function should be used with caution. By necessity, this function can
only return license text without any attribution, but most packages that use
ISC, BSD, or MIT will include copyright attribution in their license files.

* **Parameters:**
  **spdx** – The SPDX identifier of the license, or a reference returned by
  py:func:get_standard_license_reference.
* **Returns:**
  The text of the license.

### license_mole.licenses.resources.is_safe_license_text(spdx: str, attribution: list[str] | None) → bool

Identify if it is safe to use standard text for a license.

Standard text is considered “safe” if the text exists as a resource in this
module and one of the following is true:

* The license is associated with a specific, known project.
* The license text does not permit modification, so all projects using it
  : will have the same text.
* Copyright attribution has already been found from another source.

* **Parameters:**
  * **spdx** – The SPDX identifier of the license.
  * **attribution** – A list of copyright attribution lines.
* **Returns:**
  True if the standard text can be used
