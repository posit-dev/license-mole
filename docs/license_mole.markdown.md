# license_mole.markdown module

Functions for handling Markdown text.

Copyright (c) 2025 Posit Software, PBC

### *class* license_mole.markdown.MarkdownFixer(replace_underlines: bool = True, blockquote: bool = True, expect_blocks: bool = False, expect_comments: bool = False)

Bases: `object`

A class to accumulate Markdown text line-by-line.

This class generates Quarto-compatible Markdown, so it translates
formatting found in plaintext and other Markdown variations into
Quarto’s dialect. It also fixes some special cases in known text
files that cause Quarto to misrender the layout.

* **Parameters:**
  * **replace_underlines** – If True, convert underlines to headers
  * **blockquote** – If True, put the entire document in a blockquote
  * **expect_blocks** – If True, treat triple-quoted text as blockquotes
  * **expect_comments** – If True, treat /\* 

    ```
    *
    ```

    / as code comments

#### append(line: str) → None

Add a line to the document.

* **Parameters:**
  **line** – The line to append

#### clear_list()

Immediately closes all open outlines.

#### pop_list()

Decreases the current outline nesting depth.

#### push_list(list_type: str, value: str, indent: int)

Increases the current outline nesting depth.

* **Parameters:**
  * **list_type** – ‘A’, ‘1’, or ‘i’ to indicate list type
  * **value** – The first index in the list
  * **indent** – Hanging indent size, in characters

#### render() → str

Render the collected Markdown with duplicated lines removed.

* **Returns:**
  Markdown text

#### set_quote_level(amount: int)

Set the current blockquote level.

* **Parameters:**
  **amount** – The number of blockquote levels

### license_mole.markdown.auto_hyperlink(text: str) → str

Find hyperlinks and wraps them in Markdown.

Also corrects [http:foo](http:foo) and [https:foo](https:foo) to [http://foo](http://foo) and [https://foo](https://foo).

* **Parameters:**
  **text** – The body of text to search for hyperlinks
* **Returns:**
  Markdown text

### license_mole.markdown.md_link(text: str, url: str) → str

Render a Markdown link.

If the provided URL is empty, just returns plain text.

* **Parameters:**
  * **text** – The text of the link
  * **url** – The target of the link
* **Returns:**
  Markdown text

### license_mole.markdown.strip_markdown(text: str) → str

Remove Markdown formatting from a block of text.

* **Parameters:**
  **text** – Markdown text to strip
* **Returns:**
  Plain text
