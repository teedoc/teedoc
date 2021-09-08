#!/bin/bash

locales=(zh_CN ja)
for locale in ${locales[@]}
do
    echo "-- generate ${locale} mo file from po files"
    pybabel compile -d locales -l ${locale}
done

