from dataclasses import dataclass, field

from troubadour.interfaces import Button, Game, Input, TextInput
from troubadour.html_impl import Story, InfoPanel, run_game, ImagePanel
from troubadour.rich_text import RichText


@dataclass
class MyGame(Game):
    story: Story = field(default_factory=Story)
    info: InfoPanel = field(default_factory=InfoPanel)
    extra: InfoPanel = field(default_factory=InfoPanel)
    porthole: ImagePanel = field(default_factory=ImagePanel)

    def start(self) -> list[Input]:
        self.porthole.set_url("https://picsum.photos/300/350")
        self.info.set_title("Informazion")
        self.info.set_text("str: **4**\n\nagi: **2**\n\nint: **3**")
        self.extra.set_title("Egzdra")
        self.extra.set_text("things\n\nthings\n\nthings\n\nthings\n\nthings\n\nthangs")

        self.story.display(
            RichText(
                """
# Markdown test

This is a test of the **markdown capabilities** of the thing.

Please disregard {}.

## Information

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we {}?
        """
            ).format(
                RichText("actual content").tooltip("I'm a <b>tooltip</b>"),
                RichText("doomed").classes("red").tooltip("Je suis une tooltip"),
            )
        )

        self.story.image("https://picsum.photos/800/200", "image")

        return [Button("Click me", "pouac")]

    def pouic(self) -> list[Input]:
        self.story.newpage()
        self.story.display("Hello")
        self.story.image("https://picsum.photos/800/150", "image")
        return [Button("Pouac all the way", "pouac")]

    def pouac(self) -> list[Input]:
        self.story.newpage()
        self.story.display("Hello world\n\nSo great")
        return [
            Button("Pouac", "pouac"),
            TextInput("Send", "pouec", "hello world", "Type some random thing here"),
        ]

    def pouec(self, msg: str) -> list[Input]:
        self.story.newpage()
        self.story.display(f"This is the message: {msg}")
        return [
            Button("Pouac", "pouac"),
            Button("Pouic", "pouic"),
        ]


run_game(MyGame())
