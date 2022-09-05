import os, sys
import argparse
import time
from glob import glob
try:
    from .teedoc_compare import get_changed_files
except:
    from teedoc_compare import get_changed_files


cloud_help = '''
cloud service provider, different cloud service provider has different config args:
qiniu:
    --bucket: bucket name
    --access_key: access key
    --secret_key: secret key
'''

class Qiniu():
    def __init__(self, bucket, access_key, secret_key):
        import qiniu
        self.qiniu = qiniu
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

    def upload(self, file_path, key):
        fail_count = 3
        print("upload {} to {}".format(file_path, key))
        while 1:
            try:
                q = self.qiniu.Auth(self.access_key, self.secret_key)
                token = q.upload_token(self.bucket, key, 3600)
                ret, info = self.qiniu.put_file(token, key, file_path, version='v2')
                assert ret['key'] == key
                assert ret['hash'] == self.qiniu.etag(file_path)
            except Exception as e:
                fail_count -= 1
                if fail_count == 0:
                    raise e
                print("upload failed, retrying after 5s...")
                time.sleep(5)
                print("retrying...")
                continue
            if fail_count != 3:
                print("upload success")
            break

def remove_tail(path):
    if path == "/":
        return path
    if path.endswith("/"):
        return path[:-1]

def get_files(file_or_dir, old_dir):
    if os.path.isdir(file_or_dir):
        file_or_dir = remove_tail(file_or_dir)
        if not os.path.exists(file_or_dir):
            print("new directory not exists: {}".format(file_or_dir))
            sys.exit(1)
        files = []
        if old_dir:
            old_dir = remove_tail(old_dir)
            if not os.path.exists(old_dir):
                print("old directory not exists: {}".format(old_dir))
                sys.exit(1)
            new, modified, deleted = get_changed_files(old_dir, file_or_dir)
            modified.extend(new)
            for path in modified:
                files.append((os.path.join(file_or_dir, path), path))
        else:
            for path in glob(os.path.join(file_or_dir, "**"), recursive=True):
                if os.path.isfile(path):
                    files.append((path, path[len(file_or_dir)+1:]))
        return files
    else:
        if not os.path.exists(file_or_dir):
            print("File not exists: {}".format(file_or_dir))
            sys.exit(1)
        return [(file_or_dir, os.path.basename(file_or_dir))]

def main():
    parser = argparse.ArgumentParser(description="Upload files to cloud, only upload new file and modified file, won't delete file")
    parser.add_argument("--cloud", type=str, default="qiniu", help=cloud_help, choices=["qiniu"])
    parser.add_argument("--bucket", type=str, default="", help="bucket name")
    parser.add_argument("--access_key", type=str, default="", help="access key")
    parser.add_argument("--secret_key", type=str, default="", help="secret key")
    parser.add_argument("--old", type=str, default="", help="compare two directories' different files to upload")
    parser.add_argument("file_or_dir", type=str, help="file path or directory to upload, if directory, upload all files in it and won't upload the directory")
    args = parser.parse_args()

    if args.cloud == "qiniu":
        try:
            import qiniu
        except ImportError:
            print("Please install qiniu python sdk by: pip install qiniu")
            sys.exit(1)
        if (not args.bucket) or (not args.access_key) or (not args.secret_key):
            print("Please specify bucket, access_key and secret_key")
            sys.exit(1)
        uploader = Qiniu(args.bucket, args.access_key, args.secret_key)
        files = get_files(args.file_or_dir, args.old)
        print("---------------------------")
        print("{} files need to upload".format(len(files)))
        print("---------------------------")
        for abs, rel in files:
            uploader.upload(abs, rel)
        print("complete")

if __name__ == "__main__":
    main()
