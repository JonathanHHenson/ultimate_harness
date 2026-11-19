---
name: html-development
description: Write and validate HTML markup, templates, and form semantics. Use for HTML files, markup emitted by templates, and accessibility or structure changes to HTML.
---

# HTML Development

- Identify the authoring source and template syntax. Validate rendered HTML for template changes as well as the template with its configured tools. Validate embedded executable code through its own language tooling.
- Use semantic elements and the project’s document outline. Associate inputs with labels, use a fieldset and legend for related choices, and expose a useful accessible name for interactive elements.
- Run the project’s markup checker or its configured `html-validate FILES`. Use the configured formatter in check mode, such as `prettier --check FILES`. Check representative rendered pages when the source syntax is templated. [HTML Validate CLI](https://html-validate.org/usage/cli.html) · [Prettier CLI](https://prettier.io/docs/cli)
- For standalone HTML without project tooling, run [the bundled validator](scripts/validate-html.sh) with Node 24.8 or later in the 24 series and npm. Pass HTML files or quoted globs. It uses a pinned HTML Validate release.
- In the browser, verify the accessible structure, link and form semantics, keyboard order, and expected states. Exercise behavior through the project’s browser suite where available. Use representative markup with dynamic and missing data. [W3C accessibility checks](https://www.w3.org/WAI/test-evaluate/preliminary/)
