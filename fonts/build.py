#!/usr/bin/python3
import os
import shutil
import subprocess
from urllib.request import urlopen
from zipfile import ZipFile
from git import Repo

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BUILD_DIR = os.path.join(SCRIPT_DIR, "build")

# SCALABLE FONT2 TOOLS
SFN2_REPO = "https://gitlab.com/bztsrc/scalable-font2"
SFN2_LOCAL = os.path.join(BUILD_DIR, "sfn2")
SFN2_CONV = os.path.join(SFN2_LOCAL, "sfnconv", "sfnconv")

if not os.path.exists(SFN2_CONV):
    if os.path.exists(SFN2_LOCAL):
        shutil.rmtree(SFN2_LOCAL)
    os.makedirs(SFN2_LOCAL)

    print("Cloning SFN2 repository: {}".format(SFN2_REPO))
    Repo.clone_from(SFN2_REPO, SFN2_LOCAL)

    print("Building SFN2 conversion tool")
    make = subprocess.Popen("make", cwd=os.path.join(
        SFN2_LOCAL, "sfnconv"), stdout=open(os.devnull, 'wb'))
    make.wait()


def bundleFonts(input_files, out_dir, name, extra_args):
    sfn_files = []
    for file in input_files:
        sfn_file = os.path.join(out_dir, os.path.splitext(os.path.basename(file))[0] + ".sfn")
        sfn_arg_list = [SFN2_CONV]
        sfn_arg_list.extend(extra_args)
        sfn_arg_list.extend([file, sfn_file])
        sfn_conv = subprocess.Popen(sfn_arg_list)
        sfn_conv.wait()
        sfn_files.append(sfn_file)

    sfn_collection = os.path.join(out_dir, name + ".sfnc")
    sfn_arg_list = [SFN2_CONV, "-c"]
    sfn_arg_list.extend(sfn_files)
    sfn_arg_list.append(sfn_collection)
    sfn_conv = subprocess.Popen(sfn_arg_list)


# INTER FONT
INTER_NAME = "Inter"
INTER_VERSION = "3.19"
INTER_URL = "https://github.com/rsms/inter/releases/download/v{}/Inter-{}.zip".format(
    INTER_VERSION, INTER_VERSION)
INTER_OUT_PATH = os.path.join(SCRIPT_DIR, INTER_NAME)
INTER_BUILD_PATH = os.path.join(BUILD_DIR, INTER_NAME)
INTER_ZIP = os.path.join(INTER_BUILD_PATH, INTER_NAME + ".zip")

if not os.path.exists(INTER_BUILD_PATH):
    os.makedirs(INTER_BUILD_PATH)

    # Get the release from GitHub
    zipresp = urlopen(INTER_URL)
    tempzip = open(INTER_ZIP, "wb")
    tempzip.write(zipresp.read())
    tempzip.close()

    # Re-open the newly-created file with ZipFile()
    zf = ZipFile(INTER_ZIP)
    zf.extractall(path=INTER_BUILD_PATH)
    zf.close()


INTER_DESKTOP = os.path.join(INTER_BUILD_PATH, "Inter Desktop")

INTER_OTF_FILES = []
for file in os.listdir(INTER_DESKTOP):
    if os.path.isfile(os.path.join(INTER_DESKTOP, file)) and os.path.splitext(file)[1] == '.otf':
        INTER_OTF_FILES.append(os.path.join(INTER_DESKTOP, file))

bundleFonts(INTER_OTF_FILES, INTER_OUT_PATH, INTER_NAME, [])
bundleFonts(INTER_OTF_FILES, INTER_OUT_PATH + "-ascii", INTER_NAME, ["-r", "0", "128"])
