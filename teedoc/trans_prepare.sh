#!/bin/bash

echo "-- extract keys from files"
mkdir -p locales
pybabel extract -F babel.cfg -o locales/messages.pot ./

locales=(zh_CN ja)
for locale in ${locales[@]}; do
    echo "-- generate ${locale} po files from pot files"
    if [[ -f locales/${locale}/LC_MESSAGES/messages.po ]]; then
        echo "-- file already exits, only update"
        pybabel update -i locales/messages.pot -d locales -l ${locale}
    else
        echo "-- file not exits, now create"
        pybabel init -i locales/messages.pot -d locales -l ${locale}
    fi
done

