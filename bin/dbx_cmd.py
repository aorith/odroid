#!/usr/bin/env python3
import argparse
import os
import sys
import hashlib
import time
import contextlib
from datetime import datetime
from tqdm import tqdm
import dropbox

print("-------------------------------------------------------------------")
print("[" + datetime.now().strftime("%Y%m%d%H%M%S") + "] STARTING...")
print(sys.argv)
print("-------------------------------------------------------------------")

tmp_path = os.path.join(os.environ['HOME'], 'Downloads')
token_file = os.path.join(os.environ['HOME'], 'secret/api-dropbox.txt')
try:
    with open(token_file, "r") as f:
        TOKEN = f.readline().rstrip("\n")
        PASSWORD = f.readline().rstrip("\n")
except Exception:
    print("ERROR: Couldn't load token_file {}".format(token_file))

parser = argparse.ArgumentParser(
    description='Compresses and uploads selected folder to Dropbox')
parser.add_argument('-r', '--remote-folder', nargs=1, required=True,
                    help='Destination folder in your Dropbox')
parser.add_argument('-l', '--local-folder', nargs=1, required=True,
                    help='Local directory to upload')
parser.add_argument('-t', '--token', default=TOKEN,
                    help='Access token '
                    '(see https://www.dropbox.com/developers/apps)')
parser.add_argument('-m', '--max-files', nargs=1, type=int, required=True,
                    help='Maximum number of backups to store (will delete oldest)')


def md5(fname):
    fname = os.path.realpath(fname)
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(dbx, fname, dest):
    """ upload to dropbox, f = file to upload
    dest = path to upload the file, including filename """
    dest = os.path.realpath(dest)
    fname = os.path.realpath(fname)
    file_size = os.path.getsize(fname)
    chunk_size = 4 * 1024 * 1024
    with open(fname, 'rb') as f:
        if file_size <= chunk_size:
            data = f.read()
            with stopwatch('upload %d bytes' % len(data)):
                try:
                    res = dbx.files_upload(data, dest, mute=True)
                except dropbox.exceptions.ApiError as err:
                    print("*** API error ", err)
                    return None
        else:
            with tqdm(total=file_size, desc="Uploaded") as pbar:
                try:
                    upload_session_start_result = dbx.files_upload_session_start(
                        f.read(chunk_size)
                    )
                    pbar.update(chunk_size)
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=upload_session_start_result.session_id,
                        offset=f.tell(),
                    )
                    commit = dropbox.files.CommitInfo(path=dest)
                    while f.tell() < file_size:
                        if (file_size - f.tell()) <= chunk_size:
                            res = dbx.files_upload_session_finish(
                                f.read(chunk_size), cursor, commit
                            )
                        else:
                            dbx.files_upload_session_append(
                                f.read(chunk_size),
                                cursor.session_id,
                                cursor.offset,
                            )
                            cursor.offset = f.tell()
                        pbar.update(chunk_size)
                except dropbox.exceptions.ApiError as err:
                    print("ERROR: *** API error ", err)
                    return None

    print("Uploaded as", str(res.name.encode('utf8')))
    return res


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


def delete_file(dbx, f):
    f = os.path.realpath(f)
    try:
        dbx.files_delete(f)
    except Exception:
        print("ERROR: Couldn't delete the file: {}".format(f))


def list_folder(dbx, folder):
    folder = os.path.realpath(folder)
    try:
        res = dbx.files_list_folder(folder)
    except Exception:
        print("Folder '{}' doesn't exist, creating it".format(folder))
        try:
            dbx.files_create_folder(folder)
            res = dbx.files_list_folder(folder)
        except Exception:
            print("ERROR: Can't create folder {}".format(folder))
    return res


def file_exists(dbx, md5_sum, folder):
    folder = os.path.realpath(folder)
    res = list_folder(dbx, folder)
    for entry in res.entries:
        if entry.name.split("-")[1].split(".")[0] == md5_sum:
            return True
    return False


def count_of_files(dbx, folder):
    folder = os.path.realpath(folder)
    res = list_folder(dbx, folder)
    return len(res.entries)


def oldest_file(dbx, folder):
    folder = os.path.realpath(folder)
    files = []
    res = dbx.files_list_folder(folder)
    for entry in res.entries:
        files.append(entry.name)
    files.sort()
    return files[0]


args = parser.parse_args()

dbx = dropbox.Dropbox(args.token, timeout=2000)

local_folder = os.path.realpath(args.local_folder[0])
remote_folder = args.remote_folder[0].rstrip("/")
curr_time = datetime.now().strftime("%Y%m%d%H%M%S")

ext = ".tar"
compressed_name1 = curr_time + ext
compressed_name1 = os.path.join(tmp_path, compressed_name1)

# tar and calculate md5, can't find a way to have same md5 with 7zip even removing metadata also tar stores permissions
cmd = "find {} -print0 | LC_ALL=C sort -z | tar --no-recursion --null -T - -cvf {} >/dev/null 2>&1".format(
    local_folder, compressed_name1
)
os.system(cmd)
#os.system("find {} -print0 | LC_ALL=C sort -z | GZIP=-n tar --no-recursion --null -T - -zcvf {}".format(local_folder, compressed_name))

compressed_md5 = md5(compressed_name1)
if file_exists(dbx, compressed_md5, "/" + remote_folder):
    print("File with md5:{} already exists, no backup needed...".format(compressed_md5))
    os.remove(compressed_name1)
else:
    ext = ".7z"
    compressed_name = compressed_name1 + ext
    # careful, -sdel deletes files after compression
    cmd = "7z a -r -mx9 -mtm- -mtc- -mta- -t7z -sdel -y {} {} -p{}".format(
        compressed_name, compressed_name1, PASSWORD
    )
    os.system(cmd)

    new_name = curr_time + "-" + compressed_md5 + ext
    new_name = os.path.join(tmp_path, new_name)
    os.rename(compressed_name, new_name)

    print("File {} doesn't exists, uploading...".format(new_name))
    res = upload_file(
        dbx, new_name,
        "/" + remote_folder + "/" + os.path.basename(new_name)
    )
    if res is not None:
        print("File uploaded successfully to ", str(res.path_display))
    else:
        print("Failed to upload the file.")

    print("Cleaning...")
    os.remove(new_name)

# finally delete older backups if we are over the max_files limit
if count_of_files(dbx, "/" + remote_folder) > args.max_files[0]:
    file_to_delete = oldest_file(dbx, "/" + remote_folder)
    if file_to_delete.endswith(ext):
        file_path = "/" + remote_folder + "/" + file_to_delete
        print("Deleting {}...".format(file_path))
        delete_file(dbx, file_path)
    else:
        print("Tried to delete file {} but it doesn't appear to be a {} archive".format(
            file_to_delete, ext)
        )
print("-------------------------------------------------------------------")
print("[" + datetime.now().strftime("%Y%m%d%H%M%S") + "] END.")
print("-------------------------------------------------------------------")
