#!python

import os

with open("locales.cfg") as f:
    exec(f.read())

print(f"== translate locales: {locales} ==")

for locale in locales:
    print(f"-- generate {locale} mo file from po files")
    os.system(f"pybabel compile -d locales -l {locale}")

