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

from docopt import docopt

import templates

arguments = docopt(__doc__)

proj_dir = Path(arguments["<project-directory>"])
main = proj_dir / Path(arguments["<main>"])
dest = Path(arguments["--dest"])

files_to_include = list(proj_dir.rglob("[!_]*.py"))
assert main in files_to_include, "Provided main script is not in project folder!"

index_template = Template(pkg_resources.read_text(templates, "index.html"))
result = index_template.substitute(
    dict(
        file_list=",\n            ".join(f'"{str(file)}"' for file in files_to_include),
        main_file=f'"../{main}"',
    )
)

dest_index = dest / "index.html"
dest_index.parent.mkdir(parents=True, exist_ok=True)
with dest_index.open("w") as f:
    f.write(result)
