#!/bin/bash

set -e

if [[ "${1}x" != "x" ]]; then
    cd $1
fi
if [[ !-f teedoc/template/site_config.json ]]; then
    echo "submodule need pull"
    exit 1
fi
rm -rf dist build
python setup.py sdist bdist_wheel
twine upload dist/*

