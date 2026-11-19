---
name: css-development
description: Write, lint, format, and verify CSS stylesheets, responsive layouts, and visual states. Use for CSS files and styles embedded in templates or web components.
---

# CSS Development

- Read the project’s design tokens, stylesheet organization, supported browsers, and any preprocessor configuration. Keep selectors scoped to the component or behavior they style and account for cascade order, specificity, and inheritance.
- Run the project’s stylesheet linter and formatter in check mode. With Stylelint configured, pass the changed stylesheet paths to `stylelint`. With Prettier configured, run `prettier --check FILES`. For a preprocessor, run its configured build and test the generated styles. [Stylelint CLI](https://stylelint.io/user-guide/cli) · [Prettier CLI](https://prettier.io/docs/cli)
- For plain CSS without project tooling, run [the bundled checker](scripts/validate-css.sh) with Node 24.15 or later in the 24 series and npm. It uses a pinned Stylelint release and the [basic correctness rules](scripts/stylelint.json). Pass CSS files or quoted globs.
- Check rendered behavior in the project’s supported browsers at narrow and wide widths. Inspect computed styles when the cascade is uncertain. Verify overflow, focus visibility, readable contrast, and reduced-motion behavior when relevant. Use the existing browser or visual regression suite, or capture representative before and after states.
- Keep shared theme settings in the existing token system. Add only selectors and breakpoints that serve current content and interaction states.
