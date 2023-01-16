from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from types import SimpleNamespace

import mistune
from pyodide.ffi import to_js  # type: ignore
from pyodide.code import run_js  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import js  # type: ignore
from pyscript import display as psdisplay  # type: ignore
from js import tippy  # type: ignore

from troubadour.interfaces import (
    AbstractGame,
    AbstractImagePanel,
    AbstractInfoPanel,
    AbstractStory,
)
from troubadour.troubadown import troubadownify


@dataclass
class Story(AbstractStory):
    history: list[str] = field(default_factory=list)

    def _scroll_to_bottom(self) -> None:
        tgt = Element("story").element
        tgt.scrollTop = tgt.scrollHeight

    def display(
        self,
        text: str,
        markdown: bool = True,
        tooltips: Optional[list[str]] = None,
        named_tooltips: Optional[dict[str, str]] = None,
    ) -> None:
        self.history.insert(0, text)

        html, _ = troubadownify(text)

        if markdown:
            psdisplay(HTML(mistune.html(html)), target="story")
        else:
            psdisplay(HTML(html), target="story")

        class TOTO:
            def __init__(self) -> None:
                self.content = "Yolo"

        if tooltips is not None:
            i = 0
            for tt in tooltips:
                run_js(
                    f"""tippy("#troubadour_tooltip__{i}",
                            {{
                                content:"{tt}",
                                allowHTML:true,
                            }}
                        );"""
                )

                i += 1

        if named_tooltips is not None:
            i = 0
            for name, tt in named_tooltips.items():
                run_js(
                    f"""tippy("#troubadour_tooltip_{name}",
                            {{
                                content:"{tt}",
                                allowHTML:true,
                            }}
                        );"""
                )

                i += 1

        self._scroll_to_bottom()

    def newpage(self) -> None:
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")
        self._scroll_to_bottom()


if __name__ == "__main__":
    s = Story()
