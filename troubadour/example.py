from typing import Any

from pyodide.ffi import create_proxy  # type: ignore
from pyscript import Element  # type: ignore

from troubadour.pyscript_impl import Story, InfoPanel, render_panels

s = Story()

s.display(
    f"""# Markdown test

This is a test of the **markdown capabilities** of the thing.
Please disregard |lapin?actual content|.

## Information

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we |?red:doomed|?
""",
    tooltips=["I'm a <b>tooltip</b>"],
    named_tooltips={"lapin": "Je suis une tooltip"},
)

s.image("https://picsum.photos/800/200", "image")

i = InfoPanel()
i.set_title("Informazion")
i.set_text("str: **4**\n\nagi: **2**\n\nint: **3**")

e = InfoPanel()
e.set_text("things\n\nthings\n\nthings\n\nthings\n\nthings\n\nthangs")

render_panels(i, e)


def pouic(_: Any) -> None:
    s.newpage()
    s.display("Hello")


Element("click").element.addEventListener("click", create_proxy(pouic))
