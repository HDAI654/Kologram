#!/bin/sh

set -e

# Step 1: Set base project root and PYTHONPATH
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT
echo "Base PROJECT_ROOT: $PROJECT_ROOT"

# Step 2: Handle service parameter
if [ -n "$1" ]; then
    SERVICE_ROOT="$PROJECT_ROOT/$1"
    if [ -d "$SERVICE_ROOT" ]; then
        echo "Service directory found: $SERVICE_ROOT"
        PROJECT_ROOT="$SERVICE_ROOT"
        export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT
        echo "Updated PROJECT_ROOT to: $PROJECT_ROOT"
    else
        echo "Warning: Service directory '$SERVICE_ROOT' not found"
    fi
fi

# Step 3: Change to specific test directory
if [ -n "$2" ]; then
    TEST_DIR="$PROJECT_ROOT/$2"
    if [ -d "$TEST_DIR" ]; then
        echo "Changing to test directory: $TEST_DIR"
        cd "$TEST_DIR"
    else
        echo "Warning: Test directory '$TEST_DIR' not found, staying in current directory"
    fi
elif [ -n "$1" ]; then
    # If only one argument provided (service), change to service directory
    if [ -d "$PROJECT_ROOT" ]; then
        echo "Changing to service directory: $PROJECT_ROOT"
        cd "$PROJECT_ROOT"
    fi
fi

echo "Current working directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# Run pytest
python -m pytest -v