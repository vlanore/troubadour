from dataclasses import dataclass, field
from typing import Optional

import mistune

from troubadour.id import get_id


@dataclass
class RichText:
    text: str
    classes: list[str] = field(default_factory=list)
    tooltip: Optional["RichText"] = None
    args: list["RichText"] = field(default_factory=list)
    kwargs: dict[str, "RichText"] = field(default_factory=dict)

    def render(self, markdown: bool = True) -> str:
        rendered_args = [arg.render(False) for arg in self.args]
        rendered_kwargs = {key: arg.render(False) for key, arg in self.kwargs.items()}
        result = self.text.format(*rendered_args, **rendered_kwargs)
        html_params = ""
        if self.classes:
            html_params += f' class="{" ".join(self.classes)}"'
        if self.tooltip is not None:
            id = get_id()
            html_params += f' id="troubadour_tooltip_{id}"'
        if html_params != "":
            result = f"<span{html_params}>{result}</span>"
        if markdown:
            result = mistune.html(result)
        return result


if __name__ == "__main__":
    t1 = RichText(
        "Hello *world*", classes=["red", "blue"], tooltip=RichText("Hello there!")
    )
    t2 = RichText("# Hello\n\nMessage: **{}**", args=[t1])
    print(t2.render())
