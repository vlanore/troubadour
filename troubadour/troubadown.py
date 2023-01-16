import re


def troubadownify(input: str) -> tuple[str, list[str]]:
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
    next_tt_index = 0
    tooltips = []
    for match in re.finditer(whole_re, input):
        groupdict = match.groupdict()
        output += input[cursor : match.start()] + "<span "

        if groupdict["cls"]:
            output += match.expand(r' class="\g<cls>"')

        match groupdict["tt"]:
            case "":
                tooltips.append(f"_{next_tt_index}")
                output += f' id="troubadour_tooltip__{next_tt_index}"'
                next_tt_index += 1
            case None:
                pass
            case s:
                tooltips.append(s)
                output += f' id="troubadour_tooltip_{s}"'

        output += match.expand(r">\g<body></span>")
        cursor = match.end()

    output += input[cursor:]

    return output, tooltips
