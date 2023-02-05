"""Troubadour command line interface

Usage:
  troubadour make [options] <project-directory> <main>
  troubadour (-h | --help)

Options:
  -d <dir> --dest <dir>    Destination directory [default: ./build]
  -h --help                Show this screen
"""

import importlib.resources as pkg_resources
from pathlib import Path
from string import Template
import sys
from typing import Any

from docopt import docopt
from termcolor import colored

import templates


def section(text: str) -> None:
    print(colored(f"\n~ {text} ~", "blue", attrs=["bold"]))


def param(text: Any) -> str:
    return colored(str(text), "magenta")


def data(text: Any) -> str:
    return colored(str(text), "cyan")


def success(text: str) -> None:
    print(f"{text}:", colored("OK", "green"))


def error(text: str) -> None:
    print(f"{text}:", colored("Error", "red"))


arguments = docopt(__doc__)

section("Command line arguments")
proj_dir = Path(arguments["<project-directory>"])
main = proj_dir / Path(arguments["<main>"])
dest = Path(arguments["--dest"])
print(f"Project directory: {param(proj_dir)}")
print(f"Main script: {param(main)}")
print(f"Destination directory: {param(dest)}")

section("Computing list of files")
files_to_include = list(proj_dir.rglob("[!_]*.py"))
success("Getting list of python files")
print(f"Found {data(str(len(files_to_include))+' files')}")
if main in files_to_include:
    success("Main file in directory")
else:
    error("Main file in directory")
    sys.exit(1)

section("Generating index file from template")
index_template = Template(pkg_resources.read_text(templates, "index.html"))
success("Loading template")
result = index_template.substitute(
    dict(
        file_list=",\n            ".join(f'"{str(file)}"' for file in files_to_include),
        main_file=f'"../{main}"',
    )
)
success("Generate file from template")

section("Write to destination file")
dest_index = dest / "index.html"
dest_index.parent.mkdir(parents=True, exist_ok=True)
success(f"Build directory ({data(dest)})")
with dest_index.open("w") as f:
    f.write(result)
success(f"Written {data(dest_index)}")
