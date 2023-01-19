import re

from troubadour.id import get_id

# FIXME are we using the labels?
def troubadownify(input: str) -> tuple[str, dict[str | int, int]]:
    """Parses troubadown markup in input string. Returns HTML output (with classes) and
    the list of tooltip ids.

    Syntax is `|[[tooltipname]?][classname:]body|`, e.g. `|red:my text|`, `|?my text|`,
    `|tt1?my text|`, `|mytt?bold:my text|`.

    Args:
    * input (str): The text to be parsed
    """

    start = r"\|"
    tooltip = r"((?P<tt>[a-zA-Z0-9]*)\?)?"
    cls = r"((?P<cls>[a-zA-Z0-9]*)\:)?"
    body = r"(?P<body>[^|]*)"
    end = r"\|"
    whole_re = start + tooltip + cls + body + end

    output = ""
    cursor = 0
    tooltips: dict[str | int, int] = {}
    tt_count = 0
    for match in re.finditer(whole_re, input):
        groupdict = match.groupdict()
        output += input[cursor : match.start()] + '<span class="tooltip'

        if groupdict["cls"]:
            output += match.expand(r" \g<cls>")

        output += '"'

        match groupdict["tt"]:
            case "":
                id = get_id()
                tooltips[tt_count] = id
                output += f' id="troubadour_tooltip_{id}"'
                tt_count += 1
            case None:
                pass
            case s:
                id = get_id()
                tooltips[s] = id
                output += f' id="troubadour_tooltip_{id}"'

        output += match.expand(r">\g<body></span>")
        cursor = match.end()

    output += input[cursor:]

    return output, tooltips
