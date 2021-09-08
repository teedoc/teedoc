#!/bin/bash

set -e

if [[ "${1}x" != "x" ]]; then
    cd $1
fi
rm -rf dist build
python setup.py sdist bdist_wheel
twine upload dist/*

