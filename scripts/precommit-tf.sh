#!/bin/bash

TOOLS=(pylint isort black mypy)
MAX_LINE_LENGTH=140

BASEDIR=$(dirname "$0")
. $BASEDIR/precommit-common.sh

# Exit when any command fails.
set -e

check_all_tools_installed
######################################
# precommit main script.
######################################

# Move to repo root.
readonly top_dir=$(git rev-parse --show-toplevel)
cd "$top_dir" || exit 1

run_command terraform fmt "$TARGET_FILES"
