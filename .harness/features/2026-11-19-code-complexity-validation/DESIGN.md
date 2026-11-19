# Code complexity validation and language skills

## CHECK

Put the Python analyzer in the Python skill. Parse source without importing it and report functions that exceed the default limit of 10. Put a pinned ESLint complexity helper in the JavaScript skill, also with a maximum of 10. Refactor the existing violations at the responsibility boundaries of the entry points and renderers. Compare before and after outcomes to preserve behavior.

## ROUTE

Use the portable review policy for every changed executable language. Prefer project tools, fall back to the language skill or manual decision counts, and require recorded scope and results. Run the local Python, JavaScript, markup, CSS, and shell syntax commands during repository validation and in the existing packaging workflow. Verify the old complex fixtures fail and maintained sources pass.

## LANGUAGES

Route Python, JavaScript, HTML, CSS, and shell changes to separate skills. Keep reusable helpers in their corresponding skill and document configured tooling, formatting, testing, and language-specific practices. The HTML and CSS skills use pinned external analyzers for development. The shell skill uses the actual interpreter and the project’s configured shell tools. Export the packages as independent catalog components and keep all frontend runtime dependencies unchanged.

## AUTHORING

Verify the project-wide language inventory and skill coverage before running code review tools. Keep the authoring procedure and criteria with Learn and Build Skills, and route from Build Harness and the project language inventory. Carry the authoring component as a code review dependency so adopting only review still provides the procedure for filling a gap.

## RUFF

Prefer Ruff in the Python skill and use a project Ruff configuration to enable baseline lint rules and C901 with a limit of 10. Give the CI step a pinned Ruff action, version, and explicit source paths. Keep the bundled checker available for environments that lack the preferred analyzer. Verify the maintained tree and the prior complexity regression with the same Ruff version.
