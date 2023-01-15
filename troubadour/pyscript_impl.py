from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

import mistune
from pyscript import HTML  # type: ignore
from pyscript import Element  # type: ignore
from pyscript import display as psdisplay  # type: ignore

from troubadour.interfaces import (
    AbstractGame,
    AbstractImagePanel,
    AbstractInfoPanel,
    AbstractStory,
)


@dataclass
class Story(AbstractStory):
    history: list[str] = field(default_factory=list)

    def _scroll_to_bottom(self) -> None:
        tgt = Element("story").element
        tgt.scrollTop = tgt.scrollHeight

    def display(
        self, text: str, markdown: bool = True, tooltips: Optional[list[str]] = None
    ) -> None:
        self.history.insert(0, text)
        psdisplay(HTML(mistune.html(text)), target="story")
        self._scroll_to_bottom()

    def newpage(self) -> None:
        t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        psdisplay(HTML(f'<div class="divider">{t}</div>'), target="story")
        self._scroll_to_bottom()


if __name__ == "__main__":
    s = Story()
