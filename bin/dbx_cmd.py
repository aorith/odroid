#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import logging
import hashlib
import time
import psutil
from logging.handlers import RotatingFileHandler
from datetime import datetime
import dropbox

HOME = os.environ['HOME']
tmp_path = os.path.join(HOME, 'Downloads')
token_file = os.path.join(HOME, 'secret/api-dropbox.txt')

parser = argparse.ArgumentParser(
    description='Compress, encrypt and upload selected folder to Dropbox')
parser.add_argument('-r', '--remote-folder', nargs=1, required=True,
                    help='Destination folder in your Dropbox')
parser.add_argument('-l', '--local-folder', nargs=1, required=True,
                    help='Local directory to upload')
parser.add_argument('-m', '--max-files', nargs=1, type=int, required=True,
                    help='Maximum number of backups to store (will delete oldest)')
args = parser.parse_args()

logpath = filename = os.path.join(
    HOME,
    'logs',
    'dbx_cmd.py_' + args.remote_folder[0].split("/")[-1] + ".log"
)
handler = RotatingFileHandler(logpath, maxBytes=102400, backupCount=2)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Open token file
try:
    with open(token_file, "r") as f:
        TOKEN = f.readline().rstrip("\n")
        PASSWORD = f.readline().rstrip("\n")
except Exception:
    logging.error("Couldn't load token_file %s", token_file)
    exit()


def md5(fname):
    fname = os.path.realpath(fname)
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_space(dbx, file_size=None):
    sp = dbx.users_get_space_usage()
    used = sp.used
    total = sp.allocation.get_individual().allocated
    perc = round((used * 100) / total, 0)
    logging.info("Disk space used: {}/{} MBs ({}%).".format(
        round(used / (1024*1024), 2),
        round(total / (1024*1024), 2),
        perc
        )
    )
    if file_size is not None:
        if total - used < file_size:
            logging.error("Not enough free space to upload: {} MBs.".format(
                round(file_size / (1024*1024), 2)))
            exit()


def upload_file(dbx, fname, dest):
    """ upload to dropbox, f = file to upload
    dest = path to upload the file, including filename """
    dest = os.path.realpath(dest)
    fname = os.path.realpath(fname)
    file_size = os.path.getsize(fname)
    chunk_size = 4 * 1024 * 1024
    elapsed = 0
    check_space(dbx, file_size)
    with open(fname, 'rb') as f:
        if file_size <= chunk_size:
            t0 = time.time()
            try:
                res = dbx.files_upload(f.read(), dest, mute=True)
                elapsed = upload_info(file_size, f.tell(), t0, elapsed)
            except dropbox.exceptions.ApiError as err:
                logging.error("*** API error " + str(err))
                return None
        else:
            try:
                t0 = time.time()
                upload_session_start_result = dbx.files_upload_session_start(
                    f.read(chunk_size)
                )
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell(),
                )
                commit = dropbox.files.CommitInfo(path=dest)
                elapsed = upload_info(file_size, f.tell(), t0, elapsed)
                while f.tell() < file_size:
                    t0 = time.time()
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
                    elapsed = upload_info(file_size, f.tell(), t0, elapsed)
            except dropbox.exceptions.ApiError as err:
                logging.error("*** API error\n%s", err)
                return None
    return res


def upload_info(file_size, uploaded, t0, elapsed):
    t1 = time.time()
    elapsed = elapsed + (t1 - t0)
    uploaded = round(uploaded/(1024 * 1024), 2)
    file_size = round(file_size/(1024 * 1024), 2)
    msg = "Uploading {}/{} MBs done, elapsed {} seconds".format(
        uploaded, file_size, round(elapsed, 2))
    logging.info(msg)
    return elapsed


def delete_file(dbx, f):
    f = os.path.realpath(f)
    try:
        dbx.files_delete(f)
    except Exception as err:
        logging.error("Couldn't delete the file: %s\n%s", f, err)


def list_folder(dbx, folder):
    folder = os.path.realpath(folder)
    try:
        res = dbx.files_list_folder(folder)
    except Exception:
        logging.warning(
            "Folder \'%s\' doesn't exist, creating it", folder)
        try:
            dbx.files_create_folder(folder)
            res = dbx.files_list_folder(folder)
        except Exception:
            logging.error("Can't create folder %s", folder)
            exit()
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


def compress_gzip(filename):
    logging.info("Starting to gzip %s", filename)
    cmd = "gzip -9 {}".format(filename)
    print_cpu_mem_info()
    try:
        result = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
    except Exception as err:
        print_cpu_mem_info()
        logging.error("Failed to gzip file %s\n%s", filename, err)
        os.remove(filename)
        exit()

    print_cpu_mem_info()
    logging.info("Finished gzipping file.")
    return filename + '.gz'


def create_tar(path, tar_path):
    # tar and calculate md5
    logging.info("Starting to tarball the file.")
    cmd = "find {} -print0 | LC_ALL=C sort -z | tar --no-recursion --null -T - -cvf {} >/dev/null 2>&1".format(
        path, tar_path
    )
    try:
        result = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        logging.info("%s", result.decode('utf8'))
    except Exception as err:
        logging.error(
            "Process failed while trying to tar: %s\n%s", tar_path, err)
        exit()
    logging.info("Finished the tarball.")

def gpg_encrypt(filename):
    logging.info("Starting to encrypt %s", filename)
    cmd = "gpg --passphrase {} --batch --quiet --yes -c {}".format(PASSWORD, filename)
    print_cpu_mem_info()
    try:
        result = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True
            )
        logging.info("%s", result.decode('utf8'))
    except Exception as err:
        print_cpu_mem_info()
        logging.error("Process failed while trying to encrypt: %s", filename)
        exit()
    os.remove(filename)
    print_cpu_mem_info()
    logging.info("Finished encryption.")
    return filename + '.gpg'

def print_cpu_mem_info():
    vm = psutil.virtual_memory()
    memt = str(round(vm.total / (1024*1024), 2))
    memf = str(round(vm.free / (1024*1024), 2))
    memu = str(round(vm.used / (1024*1024), 2))
    memp = str(vm.percent)
    mem_string = "Total: " + memt + " Used: " + memu + " Free: " + memf + " MBs (" + memp + "%)."
    cpu = str(psutil.cpu_percent()) + '%'
    logging.info("\nMEM: %s\nCPU: %s", mem_string, cpu)


# SCRIPT START

logging.info("-----------------------------------------")
logging.info("STARTING...")
logging.info(sys.argv)
logging.info("-----------------------------------------")

dbx = dropbox.Dropbox(TOKEN, timeout=2000)

local_folder = os.path.realpath(args.local_folder[0])
remote_folder = args.remote_folder[0].rstrip("/")
curr_time = datetime.now().strftime("%Y%m%d%H%M%S")

tar_name = curr_time + '.tar'
tar_path = os.path.join(tmp_path, tar_name)

create_tar(local_folder, tar_path)
tar_md5 = md5(tar_path)

if file_exists(dbx, tar_md5, "/" + remote_folder):
    logging.info("Found md5 \"%s\" in Dropbox, no backup needed.", tar_md5)
    os.remove(tar_path)
else:
    gzipped_name = compress_gzip(tar_path)
    encrypted_name = gpg_encrypt(gzipped_name)

    ext = '.tar.gz.gpg'
    new_name = curr_time + "-" + tar_md5 + ext
    new_name = os.path.join(tmp_path, new_name)
    os.rename(encrypted_name, new_name)

    logging.info("File %s not in Dropbox, uploading...", new_name)
    res = upload_file(
        dbx,
        new_name,
        "/" + remote_folder + "/" + os.path.basename(new_name)
    )
    if res is not None:
        logging.info("File uploaded successfully to %s", res.path_display)
    else:
        logging.error("Failed to upload the file.")

    logging.info("Cleaning...")
    os.remove(new_name)

# finally delete older backups if we are over the max_files limit
if count_of_files(dbx, "/" + remote_folder) > args.max_files[0]:
    file_to_delete = oldest_file(dbx, "/" + remote_folder)
    if file_to_delete.endswith(ext):
        file_path = "/" + remote_folder + "/" + file_to_delete
        logging.info("Deleting \'%s\'...", file_path)
        delete_file(dbx, file_path)
    else:
        logging.warning("Tried to delete the file \'%s\' but it doesn't appear to be a \'%s\' archive", file_to_delete, ext)

logging.info("-----------------------------------------")
check_space(dbx)
logging.info("END.")
logging.info("-----------------------------------------")

