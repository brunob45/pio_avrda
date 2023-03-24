#!/usr/bin/env python3

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from shutil import copyfile
from urllib import request
from zipfile import ZipFile

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

# get pack list from atmel's website
print("Retrieving packs information...")
repo = "http://packs.download.atmel.com/"
index_url = repo + "index.idx"
with request.urlopen(index_url) as response:
    index = response.read()
index_root = ET.fromstring(index)

for series in ["D", "E"]:
    pkg_name = "AVR-" + series + "x_DFP"
    ns = {"atmel": "http://packs.download.atmel.com/pack-idx-atmel-extension"}
    avrdx = index_root.find('./pdsc[@atmel:name = "' + pkg_name + '"]', ns)
    version = avrdx.get("version")
    url = avrdx.get("url")
    devices = [
        device.get("name")
        for device in avrdx.findall(
            "./atmel:releases/atmel:release[1]/atmel:devices/atmel:device", ns
        )
    ]

    link = "Atmel." + pkg_name + "." + version + ".atpack"

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

    filefilter = str(AvrDaToolkitPath) + r"/(gcc|include)/.*(/specs-.*|\d+\.[aoh]$)"

    if not Path("boards").exists():
        Path("boards").mkdir()

    # find all header, linker and specs files needed for compilation
    for f in find_file(AvrDaToolkitPath, filefilter):
        boardinfo = re.match(r"^io(avr(\d+)(\w\w)(\d+))$", f.stem)
        if boardinfo:
            # create board definition file
            newboard = deepcopy(boardtemplate)
            newboard["build"]["mcu"] = boardinfo.group(1)
            board_ramsize = int(boardinfo.group(2))
            board_pincount = int(boardinfo.group(4))
            btld_ramsize = max(board_ramsize, 32)

            newboard["build"]["extra_flags"] = (
                "-DARDUINO_AVR_"
                + boardinfo.group(1).upper()
                + " -DARDUINO_avr"
                + boardinfo.group(3)
            )

            del newboard["hardware"]["millistimer"]
            # if boardinfo.group(3) == 'dd' and board_pincount <= 20:
            #     newboard["hardware"]["millistimer"] = 'B1'
            # else:
            #     newboard["hardware"]["millistimer"] = 'B2'

            if boardinfo.group(3) == "dd":
                newboard["build"]["variant"] = str(board_pincount) + "pin-ddseries"
            else:
                newboard["build"]["variant"] = str(board_pincount) + "pin-standard"

            newboard["name"] = boardinfo.group(1).upper()
            newboard["upload"]["maximum_ram_size"] = board_ramsize * 128
            newboard["upload"]["maximum_size"] = board_ramsize * 1024
            newboard["url"] = (
                "https://www.microchip.com/wwwproducts/en/" + boardinfo.group(1).upper()
            )

            if boardinfo.group(3) == "dd":
                if board_pincount == 14:
                    newboard["bootloader"]["class"] = f"optiboot_{btld_ramsize}dd14"
                else:
                    newboard["bootloader"]["class"] = f"optiboot_{btld_ramsize}dd"
            else:
                newboard["bootloader"]["class"] = f"optiboot_{btld_ramsize}dx"

            newboardfile = os.path.join("boards", boardinfo.group(1).upper() + ".json")
            with open(newboardfile, "w+") as fp:
                fp.write(json.dumps(newboard, indent=2))
                fp.write("\n")

            print_verbose("Board definition file created ->", newboardfile)

print("Success!")
