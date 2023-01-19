from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

import mistune
from pyodide.code import run_js  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import display as psdisplay  # type: ignore

from troubadour.interfaces import (
    AbstractGame,
    AbstractImagePanel,
    AbstractInfoPanel,
    AbstractStory,
)
from troubadour.troubadown import troubadownify


class InfoPanel(AbstractInfoPanel):
    def __init__(self) -> None:
        self.title: Optional[str] = None
        self.text = ""

    def set_title(self, text: str) -> None:
        self.title = text

    def get_title(self) -> Optional[str]:
        return self.title

    def set_text(self, text: str, markdown: bool = True) -> None:
        self.text = text
        self.markdown = markdown

    def get_text(self) -> tuple[str, bool]:
        return self.text, self.markdown


def render_panels(info: AbstractInfoPanel, extra: AbstractInfoPanel) -> None:
    extra_raw, extra_md = extra.get_text()
    extra_html = mistune.html(extra_raw) if extra_md else extra_raw
    Element("extra-content").element.innerHTML = extra_html

    info_raw, info_md = info.get_text()
    info_html = mistune.html(info_raw) if info_md else info_raw
    Element("info-content").element.innerHTML = info_html


def render_tooltip(id: int, text: str) -> None:
    run_js(
        f"""tippy("#troubadour_tooltip_{id}",
                {{
                    content:"{text}",
                    allowHTML:true,
                }}
            );"""
    )


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

        html, tt_labels = troubadownify(text)

        if markdown:
            psdisplay(HTML(mistune.html(html)), target="story")
        else:
            psdisplay(HTML(html), target="story")

        if tooltips is not None:
            for i, tt in enumerate(tooltips):
                render_tooltip(tt_labels[i], tt)

        if named_tooltips is not None:
            for name, tt in named_tooltips.items():
                render_tooltip(tt_labels[name], tt)

        self._scroll_to_bottom()

    def newpage(self) -> None:
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")
        self._scroll_to_bottom()

    def image(self, url: str, alt: str) -> None:
        # TODO: add to history!
        psdisplay(
            HTML(
                f"""
            <div class="card">
                <div class="card-image">
                    <figure class="image">
                    <img src="{url}" alt="{alt}">
                    </figure>
                </div>
            </div>
            """
            ),
            target="story",
        )


def add_button(
    text: str, continuation: Callable, tooltip: Optional[str] = None
) -> None:
    Element("story-interface").write(
        HTML(f'<button class="button" type="button" id="clicky">{text}</button>')
    )
    Element("clicky").element.addEventListener("click", create_proxy(continuation))


if __name__ == "__main__":
    s = Story()
    i = InfoPanel()
