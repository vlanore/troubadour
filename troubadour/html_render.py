from typing import Any, Callable

import jsonpickle as jsp
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import js  # type: ignore
from pyscript import display as psdisplay  # type: ignore


def onclick(id: str, func: Callable[[Any], None]) -> None:
    Element(id).element.addEventListener("click", create_proxy(func))


def insert_end(id: str, html: str) -> None:
    Element(id).element.insertAdjacentHTML("beforeend", html)


def set_html(id: str, html: str) -> None:
    Element(id).element.innerHTML = html


def clear(id: str) -> None:
    set_html(id, "")


def set_src(id: str, value: str) -> None:
    Element(id).element.src = value


def set_alt(id: str, value: str) -> None:
    Element(id).element.alt = value


def add_tooltip(id: int, text: str) -> None:
    run_js(
        f"""tippy("#troubadour_tooltip_{id}",
                {{
                    content:"{text}",
                    allowHTML:true,
                }}
            );"""
    )
