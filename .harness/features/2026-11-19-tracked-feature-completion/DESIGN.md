# Tracked feature completion

## TRACK

Git will track feature definitions, designs and worklogs. Keep locks and temporary transaction files ignored so a checkout receives authored records rather than process state. Preserve the history of the previously local records while replacing checkout-specific artifact paths with shareable descriptions. Keep the private originals in the session workspace.

## DOCS

Use the existing validation route before marking a feature done. Record project behavior and contracts under docs and put the durable decisions, evidence and gaps for agents under docs/agents. Link the closeout from the feature definition. Use a single consolidated summary for the already completed records and maintain a dedicated note for the current feature.

## CI

Place a read-only command under scripts that derives the repository root from its location and uses Python 3.11 TOML parsing. Report each non-DONE feature or requirement together with malformed records and unfinished status writes. Allow an empty feature store for a new project. Keep CI integration vendor-specific and outside this repository change. Verify via subprocess tests and a current-checkout run before and after closing this feature.

## DATE

Create feature directories as `YYYY-MM-DD-<slug>`. The creation command takes a lowercase kebab-case slug and prepends the current UTC date. Status and worklog commands take the full stored name, with a valid date, to address the same feature on subsequent days. Migrate existing directories using the UTC day of each first worklog entry while preserving the contents and history. The PR check continues to discover feature directories from the checkout.
