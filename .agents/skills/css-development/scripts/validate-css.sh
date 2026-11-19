#!/bin/sh
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
exec npm exec --yes --ignore-scripts --package=stylelint@18.0.0 -- stylelint --config "$script_dir/stylelint.json" "$@"
