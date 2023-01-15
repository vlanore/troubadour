from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generator

import jsonpickle as jsp
import mistune
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import js  # type: ignore
from pyscript import display as psdisplay  # type: ignore

from troubadour.pyscript_impl import Story
from troubadour.troubadown import troubadownify


s = Story()

troubadownify("Hello world, I'm a |rabbit| of life")
troubadownify("Hello world, I'm a |1?rabbit| of life")
troubadownify("Hello world, I'm a |?rabbit| of life")
troubadownify("Hello world, I'm a |red:rabbit of life|")
troubadownify("Hello world, I'm a |1?red:rabbit| of life")
troubadownify("Hello world, I'm a |1?red:rabbit| of life and |?blue:death|!")


s.display(
    f"""# Markdown test

This is a test of the **markdown capabilities** of the thing.
Please disregard actual content.

## Information

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we |?red:doomed|?
"""
)


def pouic(_: Any) -> None:
    s.newpage()
    s.display("Hello")


Element("click").element.addEventListener("click", create_proxy(pouic))
