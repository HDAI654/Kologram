#!/bin/sh

set -e

echo "========== Starting CI: running tests... =========="
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

if [ -n "$1" ]; then
    echo "Changing to directory: $1"
    cd "$1"
fi

# Run pytest
python -m pytest -v

echo "========== CI: Tests finished =========="
