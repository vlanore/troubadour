from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional, Protocol, runtime_checkable


@dataclass
class DisplayCmd:
    text: str
    markdown: bool = True
    tooltips: Optional[list[str]] = None
    named_tooltips: Optional[dict[str, str]] = None


class NewPageCmd:
    pass


@dataclass
class ImageCmd:
    url: str
    alt: str


Cmd = DisplayCmd | NewPageCmd | ImageCmd


class Story(Protocol):
    history: list[Cmd]

    @abstractmethod
    def display(
        self,
        text: str,
        markdown: bool = True,
        tooltips: Optional[list[str]] = None,
        named_tooltips: Optional[dict[str, str]] = None,
    ) -> None:
        pass

    @abstractmethod
    def newpage(self) -> None:
        pass

    @abstractmethod
    def image(self, url: str, alt: str) -> None:
        pass


class InfoPanel(Protocol):
    def get_title(self) -> Optional[str]:
        return ""

    @abstractmethod
    def get_text(self) -> tuple[str, bool]:
        pass


class ImagePanel(Protocol):
    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_alt(self) -> str:
        pass


class Input:
    pass


@runtime_checkable
class Game(Protocol):
    story: Story
    info: InfoPanel
    extra: InfoPanel
    porthole: ImagePanel

    @abstractmethod
    def start(self) -> list[Input]:
        pass


@dataclass
class Button(Input):
    text: str
    method: str
    tooltip: str = ""


@dataclass
class TextInput(Input):
    button_text: str
    method: str
    default_value: str = ""
    placeholder_text: str = ""
