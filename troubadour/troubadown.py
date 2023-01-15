import re


def troubadownify(input: str) -> tuple[str, list[str]]:
    start = r"\|"
    tooltip = r"((?P<tt>[a-zA-Z0-9]*)\?)?"
    cls = r"((?P<cls>[a-zA-Z0-9]*)\:)?"
    body = r"(?P<body>[^|]*)"
    end = r"\|"
    whole_re = start + tooltip + cls + body + end

    for match in re.finditer(whole_re, input):
        print(match.groupdict())

    return input, []
