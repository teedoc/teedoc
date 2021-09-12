#!python

import os

locales=["zh_CN", "ja"]

for locale in locales:
    print(f"-- generate {locale} mo file from po files")
    os.system(f"pybabel compile -d locales -l {locale}")

