from typing import Optional, Protocol
from dataclasses import dataclass


class Story(Protocol):
    def display(
        self, text: str, markdown: bool = True, tooltips: Optional[list[str]] = None
    ) -> None:
        raise NotImplementedError()

    def newpage(self) -> None:
        raise NotImplementedError()


class InfoPanel(Protocol):
    def get_title(self) -> str:
        raise NotImplementedError()

    def get_text(self, markdown: bool = True) -> str:
        raise NotImplementedError()


class ImagePanel(Protocol):
    def get_url(self) -> str:
        raise NotImplementedError()

    def get_alt(self) -> str:
        raise NotImplementedError()


class Game(Protocol):
    story: Story
    info: InfoPanel
    extra: InfoPanel
    porthole: ImagePanel
