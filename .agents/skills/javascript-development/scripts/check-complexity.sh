#!/bin/sh
# Run the pinned analyzer with the portable JavaScript complexity rule.
exec npm exec --yes --ignore-scripts --package=eslint@10.15.0 -- eslint \
  --no-config-lookup --no-inline-config --max-warnings 0 --rule 'complexity: [error, 10]' "$@"
