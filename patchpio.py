#!/usr/bin/env python3

import os
import re
import json
import sys

from shutil import copyfile
from pathlib import Path
from urllib import request
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from copy import deepcopy

isverbose = "-v" in sys.argv or "--verbose" in sys.argv


def print_verbose(*args):
    if isverbose:
        print(" ".join(map(str, args)))


def find_file(dir: Path, match):
    # function to find all files in a directory tree
    result = []
    for e in os.listdir(dir):
        fullpath = dir / e
        if fullpath.is_file() and re.search(match, str(fullpath)):
            result += [fullpath]
        elif fullpath.is_dir():
            result += find_file(fullpath, match)
    return result


# load template for board definition
with open("board.json") as fp:
    boardtemplate = json.load(fp)

# find platformio installation path
if "USERPROFILE" in os.environ:  # windows
    PlatformioPath = Path(os.environ["USERPROFILE"]) / ".platformio"
elif "HOME" in os.environ:  # linux
    PlatformioPath = Path(os.environ["HOME"]) / ".platformio"
else:
    PlatformioPath = Path(os.curdir)

if not PlatformioPath.exists():
    print("Cannot find Platformio at", PlatformioPath)
    exit(1)
else:
    print("Found Platformio at", PlatformioPath)

# find atmelavr toolchain
ToolchainPath = PlatformioPath / "packages/toolchain-atmelavr"
if not ToolchainPath.exists():
    pkg_install = os.system("pio pkg install -g --tool toolchain-atmelavr")
    if pkg_install != 0:
        print("Cannot find atmelavr toolchain at", ToolchainPath)
        exit(2)
else:
    print("Found toolchain at", ToolchainPath)

# get pack list from atmel's website
print("Retrieving packs information...")
repo = 'http://packs.download.atmel.com/'
index_url = repo + 'index.idx'
with request.urlopen(index_url) as response:
    index = response.read()
index_root = ET.fromstring(index)

for series in ['D', 'E']:
    pkg_name = "AVR-" + series + "x_DFP"
    ns = {'atmel': 'http://packs.download.atmel.com/pack-idx-atmel-extension'}
    avrdx = index_root.find('./pdsc[@atmel:name = "'+pkg_name+'"]', ns)
    version = avrdx.get('version')
    url = avrdx.get('url')
    devices = [device.get('name') for device in avrdx.findall(
        './atmel:releases/atmel:release[1]/atmel:devices/atmel:device', ns)]

    link = 'Atmel.' + pkg_name + '.' + version + '.atpack'

    AvrDaToolkitPack = Path(link)
    if not AvrDaToolkitPack.exists():
        print("Downloading", AvrDaToolkitPack, repo + link)
        request.urlretrieve(repo + link, AvrDaToolkitPack)
    else:
        print("Using local", AvrDaToolkitPack)

    AvrDaToolkitPack = Path(link)
    AvrDaToolkitPath = Path(AvrDaToolkitPack.stem)

    if not AvrDaToolkitPath.exists():
        print("Extracting ", AvrDaToolkitPack, "into", AvrDaToolkitPath)
        ZipFile(AvrDaToolkitPack, "r").extractall(AvrDaToolkitPath)

    print_verbose("Copying files...")

    filefilter = str(AvrDaToolkitPath) + \
        r"/(gcc|include)/.*(/specs-.*|\d+\.[aoh]$)"

    if not (PlatformioPath / "boards").exists():
        (PlatformioPath / "boards").mkdir()

    # find all header, linker and specs files needed for compilation
    for f in find_file(AvrDaToolkitPath, filefilter):
        if re.search(r".*\.h$", str(f)):  # is header file
            mynewdir = ToolchainPath / "avr/include/avr"
        elif re.search(r".*\.[ao]$", str(f)):  # is linker file
            mynewdir = ToolchainPath / "avr/lib" / str(f).split(os.sep)[-2]
        else:  # is specs file
            mynewdir = ToolchainPath / "lib/gcc/avr/"
            mynewdir /= os.listdir(mynewdir)[0]
            mynewdir /= "device-specs"

        # copy file
        copyfile(f, mynewdir / f.name)

        # remove administrator rights from file
        os.chmod(mynewdir / f.name, 420)  # 644 in octal

        print_verbose(f, "->", mynewdir)

        boardinfo = re.match(r"^io(avr(\d+)(\w\w)(\d+))$", f.stem)
        if boardinfo is not None:
            # create board definition file
            newboard = deepcopy(boardtemplate)
            newboard["build"]["mcu"] = boardinfo.group(1)
            flags = "-DARDUINO_AVR_" + \
                boardinfo.group(1).upper()+" -DARDUINO_avr"+boardinfo.group(3)
            if boardinfo.group(3) == 'dd' and int(boardinfo.group(4)) <= 20:
                flags += ' -DMILLIS_USE_TIMERB1'
            else:
                flags += ' -DMILLIS_USE_TIMERB2'
            newboard["build"]["extra_flags"] = flags
            newboard["build"]["variant"] = boardinfo.group(4)+"pin-standard"
            newboard["name"] = boardinfo.group(1).upper()
            newboard["upload"]["maximum_ram_size"] = int(
                boardinfo.group(2)) * 128
            newboard["upload"]["maximum_size"] = int(
                boardinfo.group(2)) * 1024
            newboard["url"] = "https://www.microchip.com/wwwproducts/en/" + \
                boardinfo.group(1).upper()

            if not (PlatformioPath / "boards").exists():
                (PlatformioPath / "boards").mkdir()

            newboardfile = PlatformioPath / \
                "boards" / (boardinfo.group(1).upper()+".json")
            with open(newboardfile, "w+") as fp:
                fp.write(json.dumps(newboard, indent=2))
                fp.write('\n')

            print_verbose("Board definition file created ->", newboardfile)

print("Success!")
