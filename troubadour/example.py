from dataclasses import dataclass, field
from typing import Any

from pyodide.ffi import create_proxy  # type: ignore
from pyscript import Element  # type: ignore

from troubadour.interfaces import Button, AbstractGame, AbstractInterface
from troubadour.pyscript_impl import Story, InfoPanel, run_game, ImagePanel, init_page


@dataclass
class MyGame(AbstractGame):
    story: Story = field(default_factory=Story)
    info: InfoPanel = field(default_factory=InfoPanel)
    extra: InfoPanel = field(default_factory=InfoPanel)
    porthole: ImagePanel = field(default_factory=ImagePanel)

    def start(self) -> list[AbstractInterface]:
        self.porthole.set_url("https://picsum.photos/300/350")
        self.info.set_title("Informazion")
        self.info.set_text("str: **4**\n\nagi: **2**\n\nint: **3**")
        self.extra.set_title("Egzdra")
        self.extra.set_text("things\n\nthings\n\nthings\n\nthings\n\nthings\n\nthangs")

        self.story.display(
            f"""
# Markdown test

This is a test of the **markdown capabilities** of the thing.

Please disregard |lapin?actual content|.

## Information

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we |?red:doomed|?
        """,
            tooltips=["I'm a <b>tooltip</b>"],
            named_tooltips={"lapin": "Je suis une tooltip"},
        )

        self.story.display(
            "Je suis un |?test|.\n\nJe suis |?le roi| des test.",
            tooltips=["Tooltip is life.", "tooltip is important"],
        )

        self.story.image("https://picsum.photos/800/200", "image")

        return [Button("Click me", "pouac")]

    def pouic(self) -> list[AbstractInterface]:
        self.story.newpage()
        self.story.display("Hello")
        self.story.image("https://picsum.photos/800/150", "image")
        return [Button("Pouac all the way", "pouac")]

    def pouac(self) -> list[AbstractInterface]:
        self.story.newpage()
        self.story.display("Hello world\n\nSo great")
        return [
            Button("Pouac", "pouac"),
            Button("Pouic", "pouic"),
        ]


init_page()
run_game(MyGame())
