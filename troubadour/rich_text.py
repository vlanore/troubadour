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

    def render(self, markdown: bool = True) -> tuple[str, dict[str, str]]:
        tooltips: dict[str, str] = {}
        rendered_args = []
        rendered_kwargs = {}
        for arg in self.args:
            rendered_arg, rec_tooltips = arg.render(False)
            rendered_args.append(rendered_arg)
            tooltips |= rec_tooltips
        for kw, arg in self.kwargs.items():
            rendered_arg, rec_tooltips = arg.render(False)
            rendered_kwargs[kw] = rendered_arg
            tooltips |= rec_tooltips
        result = self.text.format(*rendered_args, **rendered_kwargs)
        html_params = ""
        if self.classes:
            html_params += f' class="{" ".join(self.classes)}"'
        if self.tooltip is not None:
            id = get_id()
            html_params += f' id="troubadour_tooltip_{id}"'
            tooltips[f"troubadour_tooltip_{id}"], rec_tooltips = self.tooltip.render()
            tooltips |= rec_tooltips
        if html_params != "":
            result = f"<span{html_params}>{result}</span>"
        if markdown:
            result = mistune.html(result)
        return result, tooltips


if __name__ == "__main__":
    t1 = RichText(
        "Hello *world*", classes=["red", "blue"], tooltip=RichText("Hello there!")
    )
    t2 = RichText("# Hello\n\nMessage: **{}**", args=[t1])
    t3 = RichText("{0}\n\n{0}", args=[t2])
    print(*t3.render())
