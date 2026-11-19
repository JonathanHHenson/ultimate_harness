#!/bin/sh
exec npm exec --yes --ignore-scripts --package=html-validate@11.21.1 -- html-validate "$@"
