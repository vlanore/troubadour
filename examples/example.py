from dataclasses import dataclass, field

import troubadour as tbd
from troubadour import RichText


@dataclass
class MyGame(tbd.Game):
    story: tbd.Story = field(default_factory=tbd.Story)
    porthole: tbd.ImagePanel = field(default_factory=tbd.ImagePanel)

    def start(self) -> list[tbd.Input]:
        self.porthole.set_url("https://picsum.photos/300/350")
        # self.info.set_title("Informazion")
        # self.info.set_text("str: **4**\n\nagi: **2**\n\nint: **3**")
        # self.extra.set_title("Egzdra")
        # self.extra.set_text("things\n\nthings\n\nthings\n\nthings\n\nthings\n\nthangs")

        self.story.display(
            RichText(
                """
# Markdown test

This is a test of the **markdown capabilities** of the thing.

Please disregard {}.

## {title}

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we {}?
        """
            ).format(
                RichText("actual content").tooltip("I'm a <b>tooltip</b>"),
                RichText("doomed").classes("red").tooltip("Je suis une tooltip"),
                title=RichText("Information").classes("red"),
            )
        )

        self.story.image("https://picsum.photos/800/200", "image")

        return [tbd.Button("Click me", "pouac")]

    def pouic(self) -> list[tbd.Input]:
        self.story.newpage()
        self.story.display("Hello")
        self.story.image("https://picsum.photos/800/150", "image")
        return [tbd.Button("Pouac all the way", "pouac")]

    def pouac(self) -> list[tbd.Input]:
        self.story.newpage()
        self.story.display("Hello world\n\nSo great")
        return [
            tbd.Button("Pouac", "pouac"),
            tbd.TextInput(
                "Send", "pouec", "hello world", "Type some random thing here"
            ),
        ]

    def pouec(self, msg: str) -> list[tbd.Input]:
        self.story.newpage()
        self.story.display(f"This is the message: {msg}")
        return [
            tbd.Button("Pouac", "pouac"),
            tbd.Button("Pouic", "pouic"),
        ]


tbd.run_game(MyGame())
