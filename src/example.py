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


def display(txt: str) -> None:
    t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")
    psdisplay(HTML(mistune.html(txt)), target="story")
    tgt = Element("story").element
    tgt.scrollTop = tgt.scrollHeight


display(
    f"""# Markdown test

This is a test of the **markdown capabilities** of the thing.
Please disregard actual content.

## Information

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we |?red:doomed|?
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
