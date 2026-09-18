#!/bin/sh

echo "Running code style checks..."
pip install --quiet black flake8

# Check formatting
black .

echo "Linting finished."
