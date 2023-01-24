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


class AbstractStory(Protocol):
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


class AbstractInfoPanel(Protocol):
    def get_title(self) -> Optional[str]:
        return ""

    @abstractmethod
    def get_text(self) -> tuple[str, bool]:
        pass


class AbstractImagePanel(Protocol):
    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_alt(self) -> str:
        pass


class AbstractInterface(Protocol):
    pass


@runtime_checkable
class AbstractGame(Protocol):
    story: AbstractStory
    info: AbstractInfoPanel
    extra: AbstractInfoPanel
    porthole: AbstractImagePanel

    @abstractmethod
    def start(self) -> list[AbstractInterface]:
        pass


@dataclass
class Button(AbstractInterface):
    text: str
    method: str
    tooltip: str = ""
