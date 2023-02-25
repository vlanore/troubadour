from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional, Any

import mistune

from troubadour.id import get_id


@dataclass
class RichText:
    _text: str
    _classes: list[str] = field(default_factory=list)
    _tooltip: Optional["RichText"] = None
    _args: list["RichText"] = field(default_factory=list)
    _kwargs: dict[str, "RichText"] = field(default_factory=dict)

    def render(self, markdown: bool = True) -> tuple[str, dict[str, str]]:
        tooltips: dict[str, str] = {}
        rendered_args = []
        rendered_kwargs = {}
        for arg in self._args:
            rendered_arg, rec_tooltips = arg.render(False)
            rendered_args.append(rendered_arg)
            tooltips |= rec_tooltips
        for kw, arg in self._kwargs.items():
            rendered_arg, rec_tooltips = arg.render(False)
            rendered_kwargs[kw] = rendered_arg
            tooltips |= rec_tooltips
        result = self._text.format(*rendered_args, **rendered_kwargs)
        html_params = ""
        if self._classes:
            html_params += f' class="{" ".join(self._classes)}"'
        if self._tooltip is not None:
            id = get_id()
            html_params += f' id="troubadour_tooltip_{id}"'
            tooltips[f"troubadour_tooltip_{id}"], rec_tooltips = self._tooltip.render()
            tooltips |= rec_tooltips
        if html_params != "":
            result = f"<span{html_params}>{result}</span>"
        if markdown:
            result = mistune.html(result)
        return result, tooltips

    def classes(self, *classes: str) -> "RichText":
        result = deepcopy(self)
        result._classes += classes
        return result

    def tooltip(self, tooltip: "str | RichText") -> "RichText":
        result = deepcopy(self)
        match tooltip:
            case RichText():
                result._tooltip = tooltip
            case str():
                result._tooltip = RichText(tooltip)
        return result

    def format(self, *args: Any, **kwargs: Any) -> "RichText":
        result = deepcopy(self)
        for arg in args:
            match arg:
                case RichText():
                    result._args.append(arg)
                case _:
                    result._args.append(RichText(str(arg)))
        for key, arg in kwargs.items():
            match arg:
                case RichText():
                    result._kwargs[key] = arg
                case _:
                    result._kwargs[key] = RichText(str(arg))
        return result


if __name__ == "__main__":
    t1 = RichText("Hello *world*").classes("red", "blue").tooltip("Hello there!")
    t2 = RichText("# Hello\n\nMessage: **{}**").format(t1)
    t3 = RichText("{0}\n\n{1}").format(t2, t1)
    print(*t3.render())
