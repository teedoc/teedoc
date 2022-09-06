import os, sys
from glob import glob
import argparse
import json

def get_files(dir):
    files = []
    files_raw = glob(f"{dir}/**", recursive=True)
    for path in files_raw:
        if os.path.isfile(path):
            files.append(path[len(dir)+1:])
    return files

def is_content_different(path1, path2):
    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        return f1.read() != f2.read()

def remove_tail(path):
    if path == "/":
        return path
    if path.endswith("/"):
        return path[:-1]
    return path

def get_changed_files(old, new):
    old = remove_tail(old)
    new = remove_tail(new)
    new_files = []
    modified_files = []
    deleted_files = []
    old_dir_files = get_files(old)
    new_dir_files = get_files(new)
    flags = {}
    for path in old_dir_files:
        flags[path] = False
    for file in new_dir_files:
        # new file
        if file not in old_dir_files:
            new_files.append(file)
            continue
        # for find deleted file
        flags[file] = True
        # changed file
        different = is_content_different(os.path.join(old, file), os.path.join(new, file))
        if different:
            modified_files.append(file)
            continue
    for path, exists in flags.items():
        if not exists:
            deleted_files.append(path)

    return new_files, modified_files, deleted_files

def output_text(new, modified):
    out = ""
    for path in new:
        out += f'"{path}" '
    for path in modified:
        out += f'"{path}" '
    return out

description = '''
Compare two directories' different files.
Can be used to compare two time's build output.
'''

def main():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-f", "--format", type=str, default="json", help="output format", choices=["json", "text"])
    parser.add_argument("old_path", help="old directory")
    parser.add_argument("new_path", help="new directory")
    args = parser.parse_args()

    if not os.path.isdir(args.old_path):
        print("Path should be directory: {}".format(args.old_path))
        sys.exit(1)
    if not os.path.isdir(args.new_path):
        print("Path should be directory: {}".format(args.new_path))
        sys.exit(1)

    new, modified, deleted = get_changed_files(args.old_path, args.new_path)
    output = {
        "new": new,
        "modified": modified,
        "deleted": deleted
    }
    if args.format == "json":
        output = json.dumps(output)
    else:
        output = output_text(new, modified)
    print(output)


if __name__ == "__main__":
    main()
