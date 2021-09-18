#!python
import os

with open("locales.cfg") as f:
    exec(f.read())

print(f"== translate locales: {locales} ==")

print("-- extract keys from files")
if not os.path.exists("locales"):
    os.makedirs("locales")
os.system("pybabel extract -F babel.cfg -o locales/messages.pot ./")


for locale in locales:
    print(f"-- generate {locale} po files from pot files")
    if os.path.exists(f'locales/{locale}/LC_MESSAGES/messages.po'):
        print("-- file already exits, only update")
        os.system(f"pybabel update -i locales/messages.pot -d locales -l {locale}")
    else:
        print("-- file not exits, now create")
        os.system(f"pybabel init -i locales/messages.pot -d locales -l {locale}")


