#!/usr/bin/env python3

import os
import re
import json

from shutil import copyfile
from pathlib import Path

# load template for board definition
boardtemplate = json.load(open("board.json"))

# find platformio installation path
PlatformioPath = Path(os.environ["USERPROFILE"]) / ".platformio"
ToolchainPath = PlatformioPath / "packages/toolchain-atmelavr"

if not ToolchainPath.exists():
    print("Cannot find Platformio at", ToolchainPath)
    exit(1)
else:
    print("Found Platformio at", ToolchainPath)

# find Atmel Studio installation path
AvrDaToolkitPath = Path(
    os.environ["PROGRAMFILES(X86)"]) / "Atmel/Studio/7.0/packs/atmel/AVR-Dx_DFP"
AvrDaToolkitPath /= os.listdir(AvrDaToolkitPath)[-1]

if not AvrDaToolkitPath.exists():
    print("Cannot find Atmel Studio 7.0 at", AvrDaToolkitPath)
    exit(2)
else:
    print("Found Atmel Studio 7.0 at", AvrDaToolkitPath)


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


# find all header, linker and specs files needed for compilation
for f in find_file(AvrDaToolkitPath, r"\\(gcc|include)\\.*(\\specs-.*|\d+\.[aoh]$)"):

    isHeader = False
    if re.search(r".*\.h$", str(f)):  # is header file
        mynewdir = ToolchainPath / "avr/include/avr"
        isHeader = True
    elif re.search(r".*\.[ao]$", str(f)):  # is linker file
        mynewdir = ToolchainPath / "avr/lib" / str(f).split(os.sep)[-2]
    else:  # is specs file
        mynewdir = ToolchainPath / "lib/gcc/avr/5.4.0/device-specs"

    # create new directory
    if not mynewdir.exists():
        mynewdir.mkdir()

    # copy file
    copyfile(f, mynewdir / f.name)

    # remove administrator rights from file
    (mynewdir / f.name).chmod(644)

    if isHeader:
        # create board definition file
        boardinfo = re.match(r"^io(avr(\d+)d(\w)(\d+))$", f.stem)
        boardtemplate["build"]["mcu"] = boardinfo.group(1)
        boardtemplate["name"] = boardinfo.group(1).upper()
        boardtemplate["upload"]["maximum_ram_size"] = int(
            boardinfo.group(2)) * 128
        boardtemplate["upload"]["maximum_size"] = int(
            boardinfo.group(2)) * 1024
        boardtemplate["url"] = re.sub(
            r"/avr\d+d[ab]\d+$", "/"+boardinfo.group(1), boardtemplate["url"])

        if not (PlatformioPath / "boards").exists():
            (PlatformioPath / "boards").mkdir()

        json.dump(boardtemplate, open(PlatformioPath / "boards" /
                                      (boardinfo.group(1)+".json"), "w+"), indent=4)
