from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from troubadour.rich_text import RichText


@dataclass
class DisplayCmd:
    text: RichText


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
    def display(self, text: str | RichText) -> None:
        pass

    @abstractmethod
    def newpage(self) -> None:
        pass

    @abstractmethod
    def image(self, url: str, alt: str) -> None:
        pass


class InfoPanel(Protocol):
    def get_title(self) -> Optional[RichText]:
        return None

    @abstractmethod
    def get_text(self) -> RichText:
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
    info: Optional[InfoPanel] = None
    porthole: Optional[ImagePanel] = None

    @abstractmethod
    def start(self) -> list[Input]:
        pass


@dataclass
class Button(Input):
    text: str
    method: str
    tooltip: Optional[str | RichText] = None


@dataclass
class TextInput(Input):
    button_text: str
    method: str
    default_value: str = ""
    placeholder_text: str = ""
    tooltip: Optional[str | RichText] = None


Inputs = list[Input]
