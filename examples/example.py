from dataclasses import dataclass, field

import troubadour as tbd
from troubadour import RichText


@dataclass
class MyGame(tbd.Game):
    story: tbd.Story = field(default_factory=tbd.Story)
    # porthole: tbd.ImagePanel = field(default_factory=tbd.ImagePanel)
    info: tbd.InfoPanel = field(default_factory=lambda: tbd.InfoPanel(RichText("")))

    def start(self) -> list[tbd.Input]:
        # self.porthole.set_url("https://picsum.photos/300/350")
        # self.info.set_title("Informazion")
        self.info.set_text(
            RichText("str: **{}**\n\nagi: **2**\n\nint: **3**").format(
                RichText("4").classes("red").tooltip("Strength")
            )
        )

        self.story.display(
            RichText(
                """
# Markdown test

Sed neque quam, porttitor vitae mattis quis, efficitur sit amet enim. Nullam sit amet
orci ut lacus pharetra tristique. Suspendisse posuere id elit at mattis. Maecenas erat
est, euismod nec nulla eu, mattis pharetra arcu. Sed eget sapien id tortor lacinia
laoreet ut a mauris. Nam vel consectetur erat. Fusce eu metus lacus. Ut vitae lacus in
diam vulputate laoreet. Ut pulvinar sit amet arcu nec maximus. Nulla bibendum, nulla eu
vestibulum tempor, ipsum tellus rutrum risus, eget elementum metus ex et neque. Class
aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.
Fusce id lacinia metus, nec tristique felis. Vivamus sed risus lobortis, sodales erat
vitae, sollicitudin tortor. Donec vitae congue massa.

Morbi at interdum dolor. Duis et maximus dolor. Fusce lobortis sit amet eros ac
molestie. Phasellus ligula ipsum, congue at purus eget, tempus interdum orci. Nullam sit
amet urna turpis. Mauris scelerisque eu odio quis porta. Donec rutrum in lacus eget
volutpat. Donec placerat molestie bibendum. Nam pharetra at massa tempus euismod.
Suspendisse eget turpis eget sem lacinia vestibulum id ut purus. Phasellus aliquet diam
eu laoreet rutrum. In eleifend rhoncus ante, eu aliquam dui consequat eget. Sed eu nunc
sit amet arcu laoreet congue. Nam ut nulla massa. Vivamus vel diam vel ipsum molestie
rutrum. Vivamus at arcu felis.

## Subtitle

This is a test. Or is it? What happens if it isn't? Who could have predicted this
situation? Are we {}?
        """
            ).format(
                RichText("doomed").classes("red").tooltip("Je suis une tooltip"),
            )
        )

        self.story.image("https://picsum.photos/800/200", "image")

        return [tbd.Button("Click me", "pouac")]

    def pouic(self) -> list[tbd.Input]:
        self.story.newpage()
        self.story.display("Hello")
        self.story.image("https://picsum.photos/800/150", "image")
        self.info.set_title("Informazion")
        return [tbd.Button("Pouac all the way", "pouac")]

    def pouac(self) -> list[tbd.Input]:
        self.porthole = None
        self.story.newpage()
        self.info.set_title(None)
        self.story.display(
            """Quisque nunc tortor, finibus eu gravida quis, tristique at enim.
            Vestibulum imperdiet tempus accumsan. Sed ultricies enim a mattis pretium.
            Curabitur eu sem ac urna suscipit tincidunt eu in dui. Phasellus pharetra
            diam urna, sit amet sodales lectus dignissim eget. Sed fringilla porta
            pulvinar. Mauris eleifend dui eu finibus pretium. Morbi turpis quam,
            sollicitudin a justo sit amet, vulputate ultrices nunc. Fusce maximus
            tristique erat vitae ultrices. Aenean euismod pellentesque erat quis
            egestas. Aliquam erat volutpat."""
        )
        return [
            tbd.Button("Pouac", "pouac"),
            tbd.TextInput(
                "Send", "pouec", "hello world", "Type some random thing here"
            ),
        ]

    def pouec(self, msg: str) -> list[tbd.Input]:
        self.porthole = tbd.ImagePanel()
        self.porthole.set_url("https://picsum.photos/300/350")
        self.story.newpage()
        self.story.display(f"This is the message: {msg}")
        return [
            tbd.Button("Pouac", "pouac"),
            tbd.Button("Pouic", "pouic"),
        ]


tbd.run_game(MyGame())
