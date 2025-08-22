<a id="module-license_mole.markdown"></a>

<a id="license-mole-markdown-module"></a>

# license_mole.markdown module

Functions for handling Markdown text.

Copyright (c) 2025 Posit Software, PBC

<a id="license_mole.markdown.MarkdownFixer"></a>

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

<a id="license_mole.markdown.MarkdownFixer.append"></a>

#### append(line: str) → None

Add a line to the document.

* **Parameters:**
  **line** – The line to append

<a id="license_mole.markdown.MarkdownFixer.clear_list"></a>

#### clear_list()

Immediately closes all open outlines.

<a id="license_mole.markdown.MarkdownFixer.pop_list"></a>

#### pop_list()

Decreases the current outline nesting depth.

<a id="license_mole.markdown.MarkdownFixer.push_list"></a>

#### push_list(list_type: str, value: str, indent: int)

Increases the current outline nesting depth.

* **Parameters:**
  * **list_type** – ‘A’, ‘1’, or ‘i’ to indicate list type
  * **value** – The first index in the list
  * **indent** – Hanging indent size, in characters

<a id="license_mole.markdown.MarkdownFixer.render"></a>

#### render() → str

Render the collected Markdown with duplicated lines removed.

* **Returns:**
  Markdown text

<a id="license_mole.markdown.MarkdownFixer.set_quote_level"></a>

#### set_quote_level(amount: int)

Set the current blockquote level.

* **Parameters:**
  **amount** – The number of blockquote levels

<a id="license_mole.markdown.auto_hyperlink"></a>

### license_mole.markdown.auto_hyperlink(text: str) → str

Find hyperlinks and wraps them in Markdown.

Also corrects [http:foo](http:foo) and [https:foo](https:foo) to [http://foo](http://foo) and [https://foo](https://foo).

* **Parameters:**
  **text** – The body of text to search for hyperlinks
* **Returns:**
  Markdown text

<a id="license_mole.markdown.md_link"></a>

### license_mole.markdown.md_link(text: str, url: str) → str

Render a Markdown link.

If the provided URL is empty, just returns plain text.

* **Parameters:**
  * **text** – The text of the link
  * **url** – The target of the link
* **Returns:**
  Markdown text

<a id="license_mole.markdown.strip_markdown"></a>

### license_mole.markdown.strip_markdown(text: str) → str

Remove Markdown formatting from a block of text.

* **Parameters:**
  **text** – Markdown text to strip
* **Returns:**
  Plain text
