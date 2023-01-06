from dataclasses import dataclass
from typing import Any, Generator

import jsonpickle as jsp
import mistune
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import js  # type: ignore
from pyscript import display as psdisplay  # type: ignore


def display(txt: str) -> None:
    psdisplay(HTML(mistune.html(txt)), target="main")
    tgt = Element("main").element
    tgt.scrollTop = tgt.scrollHeight


display(
    f"""# Markdown test
    
This is a test[^1] of the **markdown capabilities** of the thing.
Please disregard actual //red:content/?.

[^1]: footnote content
"""
)


@dataclass
class State:
    i: int = 0


def main(s: State) -> Generator:
    while True:
        display(f"A ({s.i})")
        yield
        display(f"B ({s.i})")
        yield
        display(f"C ({s.i})")
        yield
        display(f"D ({s.i})")
        yield


STATE = State()
MAIN = main(STATE)


def pouic(_: Any) -> None:
    STATE.i += 1
    next(MAIN)
    # js.console.log(jsp.encode(STATE))
    js.localStorage.setItem("state", jsp.encode(STATE))


Element("click").element.addEventListener("click", create_proxy(pouic))
