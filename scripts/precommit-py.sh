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
# All python imports are based on the repo root.
readonly top_dir=$(git rev-parse --show-toplevel)
cd "$top_dir" || exit 1

run_command pylint -rn -sn --rcfile="${top_dir}"/.pylintrc "$TARGET_FILES"
run_command mypy --no-strict-optional "$TARGET_FILES"
run_command isort -p data --profile=google "$TARGET_FILES"
run_command black --line-length "$MAX_LINE_LENGTH" "$TARGET_FILES"
