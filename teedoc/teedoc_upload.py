import os, sys
import argparse
import time
from glob import glob
from progress import bar, spinner
try:
    from .teedoc_compare import get_changed_files
except:
    from teedoc_compare import get_changed_files


class Qiniu():
    def __init__(self, bucket, access_key, secret_key):
        import qiniu
        self.qiniu = qiniu
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

    def upload(self, file_path, key):
        fail_count = 3
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

class Tencentcloud_Uploader():
    def __init__(self, region, bucket, secret_id, secret_key, token, timeout = 256):
        '''
            @param timeout: 上传超时时间，单位秒
        '''
        import qcloud_cos
        self.qloud_cos = qcloud_cos
        self.region = region
        self.bucket = bucket
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.token = token
        # init SDK
            # disable logging
        import logging
        for k in logging.Logger.manager.loggerDict.keys():
            if k.startswith("qcloud_cos"):
                log = logging.getLogger(k)
                log.level = 9999
        try:
            self.client = self._get_client(self.region, self.secret_id, self.secret_key, self.token, timeout)
        except Exception as e:
            log.d("Init tencentcloud client fail, error: {}".format(e))
            raise Internal_Error("upload init fail")

    def _get_client(self, region, secret_id, secret_key, token, timeout):
        config = self.qloud_cos.CosConfig(
            Region = region,
            SecretId = secret_id,
            SecretKey = secret_key,
            Token = token,
            Scheme = "https",
            Timeout = timeout
        )

        return self.qloud_cos.CosS3Client(config)

    def close(self):
        try:
            self.client.shutdown()
        except Exception:
            pass

    def upload(self, file_path, key, progress_callback = None):
        if not os.path.exists(file_path):
            raise Exception("upload file not exist")
        try:
            rsp = self.client.upload_file(
                Bucket=self.bucket,
                Key=key,
                LocalFilePath=file_path,
                EnableMD5=False,
                MAXThread=10,
                progress_callback=progress_callback
            )
        except Exception as e:
            print("tencentcloud upload fail, error: {}".format(e))
            raise Exception("upload execute fail")

def remove_tail(path):
    if path == "/":
        return path
    if path.endswith("/"):
        return path[:-1]
    return path

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

class Progress_Bar_Raw():
    def __init__(self, name, max, interval = 1):
        self.name = name
        self.max = max
        self.interval = interval
        self.current = 0
        self.last = 0

    def next(self, n = 1):
        self.current += n
        if self.last == 0:
            self.last = time.time()
            return
        if time.time() - self.last > self.interval:
            print("{}: {:3.2f}% ({}/{})".format(self.name, self.current / self.max * 100, self.current, self.max), flush=True)
            self.last = time.time()

cloud_help = '''
cloud service provider, different cloud service provider has different dependence and config args:
qiniu:
    dependences:
        pip install qiniu
    args:
        --bucket: bucket name
        --access_key: access key
        --secret_key: secret key
tencent:
    dependences:
        pip install cos-python-sdk-v5
    args:
        --region: server region. e.g. ap-guangzhou
        --bucket: bucket name
        --secret_id: user secret id
        --secret_key: user secret key
        --token: token, optional
'''

def main():
    parser = argparse.ArgumentParser(description="Upload files to cloud, only upload new file and modified file, won't delete file")
    parser.add_argument("--cloud", type=str, default="tencent", help=cloud_help, choices=["qiniu", "tencent"])
    parser.add_argument("--bucket", type=str, default="", help="bucket name")
    parser.add_argument("--access_key", type=str, default="", help="access key")
    parser.add_argument("--secret_key", type=str, default="", help="secret key")
    parser.add_argument("--secret_id", type=str, default=None, help="secret id")
    parser.add_argument("--token", type=str, default="", help="token")
    parser.add_argument("--timeout", type=int, default=256, help="http request timeout, unit second")
    parser.add_argument("--region", type=str, default="", help="server region")
    parser.add_argument("--progress", type=str, default="bar", help="progress bar style, bar or spinner", choices=["bar", "chargingbar", "incrementalbar", "spinner", "raw"])
    parser.add_argument("--progress-interval", type=float, default=5, help="progress print interval, only for raw progress")
    parser.add_argument("--old", type=str, default="", help="compare two directories' different files to upload")
    parser.add_argument("file_or_dir", type=str, help="file path or directory to upload, if directory, upload all files in it and won't upload the directory")
    args = parser.parse_args()

    progress_classes = {
        "bar": bar.Bar,
        "chargingbar": bar.ChargingBar,
        "incrementalbar": bar.IncrementalBar,
        "spinner": spinner.Spinner,
        "raw": Progress_Bar_Raw
    }

    files = get_files(args.file_or_dir, args.old)
    print("---------------------------")
    print("{} files need to upload".format(len(files)))
    print("---------------------------", flush=True)
    progress_bar = progress_classes[args.progress]("uploading", max=len(files), interval=args.progress_interval)
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

        for abs, rel in files:
            uploader.upload(abs, rel)
            progress_bar.next()
        print("")
    elif args.cloud == "tencent":
        try:
            import qcloud_cos
        except ImportError:
            print("Please install qiniu python sdk by: pip install cos-python-sdk-v5")
            sys.exit(1)
        if (not args.region) or (not args.bucket) or (not args.secret_id) or (not args.secret_key):
            print("Please specify region bucket, secret_id and secret_key")
            sys.exit(1)
        uploader = Tencentcloud_Uploader(args.region, args.bucket, args.secret_id, args.secret_key, args.token, args.timeout)

        for abs, rel in files:
            uploader.upload(abs, rel)
            progress_bar.next()
    print("upload complete")

if __name__ == "__main__":
    main()
