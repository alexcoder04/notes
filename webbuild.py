#!/usr/bin/env python3

from datetime import datetime
import os
import shutil
import subprocess
import sys

SRC = "./src"
BUILD = "./build"
TEMPLATE = "./_template"


def touch(path: str) -> None:
    with open(path, "w") as f:
        f.write("")


def read(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def clean() -> None:
    print("Cleaning build folder")
    try:
        shutil.rmtree(BUILD)
    except FileNotFoundError:
        pass


def getsize(path: str) -> str:
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    def get_directory_size(directory):
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    if os.path.exists(path):
        if os.path.isfile(path):
            size = os.path.getsize(path)
        elif os.path.isdir(path):
            size = get_directory_size(path)
        else:
            return "---"
        return format_size(size)
    else:
        return "---"


def build_folder(folder: str) -> None:
    print(f"Start building '{folder}'")
    # prepare
    try:
        os.makedirs(f"{BUILD}/{folder}")
    except FileExistsError:
        pass
    if not os.path.isfile(f"{SRC}/{folder}/index.p.html"):
        touch(f"{SRC}/{folder}/index.p.html")
    # write index
    with open(f"{BUILD}/{folder}/index.html", "w") as f:
        f.write(read(f"{TEMPLATE}/html/header.p.html"))
        f.write(read(f"{SRC}/{folder}/index.p.html"))
        f.write(read(f"{TEMPLATE}/html/middle.p.html"))
        f.write("<p>")
        path = folder.split("/")
        for i in range(len(path)):
            f.write(f" <a href='{'/'.join(path[:i+1]) if i > 0 else '/'}'>{path[i] if path[i] != '' else '🏠 '}</a> /")
        f.write("</p>")
        f.write("<table><tbody>")
        if folder != "":
            f.write(f"<li><a href='{folder}/..'>⇑ up</a></li>")
        items = os.listdir(f"{SRC}/{folder}")
        items.sort()
        for item in items:
            if item == "index.p.html":
                continue
            target = ""
            if os.path.isfile(f"{SRC}/{folder}/{item}"):
                target = "target='blank'"
            mtime = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M", "--", f"{SRC}/{folder}/{item}"], capture_output=True, text=True).stdout.strip()
            size = getsize(f"{SRC}/{folder}/{item}")
            f.write(f"<tr><td><a href='{folder}/{item}' {target}>{item}</a></td><td>{mtime}</td><td>{size}</td></li>")
        f.write("</tbody></table>")
        f.write(read(f"{TEMPLATE}/html/footer.p.html"))
    # write other files
    for item in os.listdir(f"{SRC}/{folder}"):
        if os.path.isdir(f"{SRC}/{folder}/{item}"):
            build_folder(f"{folder}/{item}")
            continue
        if item == "index.p.html":
            continue
        if item.endswith(".p.html"):
            with open(f"{BUILD}/{folder}/{item.removesuffix('.p.html')}.html", "w") as f:
                f.write(read(f"{TEMPLATE}/html/header.p.html"))
                f.write(read(f"{SRC}/{folder}/{item}"))
                f.write(read(f"{TEMPLATE}/html/footer.html"))
            continue
        shutil.copy(f"{SRC}/{folder}/{item}", f"{BUILD}/{folder}/{item}")
    print(f"Finished building '{folder}'")


def build() -> None:
    # prepare
    os.makedirs(BUILD)
    # build
    build_folder("")
    # style
    os.makedirs(f"{BUILD}/.styling")
    for item in os.listdir(f"{TEMPLATE}/css"):
        if item.endswith(".css"):
            shutil.copy(f"{TEMPLATE}/css/index.css", f"{BUILD}/.styling/index.css")


if __name__ == "__main__":
    try:
        match sys.argv[1]:
            case "build":
                build()
            case "clean":
                clean()
            case _:
                print("Invalid argument.")
                sys.exit(1)
    except IndexError:
        print("Invalid argument.")
        sys.exit(1)

